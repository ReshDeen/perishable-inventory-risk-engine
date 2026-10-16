"""
P.I.R.E. Model Inference Module
Loads serialized XGBoost model artifact and performs calibrated probability predictions.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MODELS_DIR, RISK_LEVELS
from src.feature_engineering import FeatureEngineer
from src.model_training import ModelTrainer


class RiskPredictor:
    """Provides inference routines using the trained XGBoost pipeline."""

    def __init__(self, model_dir: Path = MODELS_DIR):
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / ModelTrainer.MODEL_FILENAME
        self.prep_path = self.model_dir / ModelTrainer.PREPROCESSOR_FILENAME
        self.meta_path = self.model_dir / ModelTrainer.METADATA_FILENAME

        self.bundle: Optional[Dict[str, Any]] = None
        self.preprocessor = None
        self.metadata: Optional[Dict[str, Any]] = None
        self.is_loaded = False
        self.load_error: Optional[str] = None

        self._try_load()

    def _try_load(self) -> bool:
        """Attempts to load model bundle and preprocessor."""
        if not self.model_path.exists() or not self.prep_path.exists():
            self.load_error = f"Model artifacts not found in '{self.model_dir}'. Model training is required."
            self.is_loaded = False
            return False

        try:
            self.bundle = joblib.load(self.model_path)
            self.preprocessor = joblib.load(self.prep_path)
            if self.meta_path.exists():
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            self.is_loaded = True
            self.load_error = None
            return True
        except Exception as e:
            self.load_error = f"Failed to load model artifacts: {str(e)}"
            self.is_loaded = False
            return False

    def predict(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, Optional[str]]:
        """
        Runs inference on given dataset.

        Returns:
            success: bool
            results_df: DataFrame with appended columns:
                - `ml_predicted_class`: numeric class code
                - `ml_predicted_risk`: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'EXPIRED'
                - `ml_confidence`: float (0.0 to 1.0)
                - `ml_class_probabilities`: dict of {RiskLevel: prob}
            error_message: Optional error string
        """
        if not self.is_loaded:
            if not self._try_load():
                return False, df, self.load_error

        try:
            fe = FeatureEngineer()
            enriched_df = fe.derive_features(df)
            X = self.preprocessor.transform(enriched_df)

            model = self.bundle["model"]
            inv_class_map = self.bundle["inv_class_map"]
            num_classes = self.bundle["num_classes"]

            # Predict probabilities
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X)
                pred_mapped = np.argmax(probs, axis=1)
                confidences = np.max(probs, axis=1)
            else:
                pred_mapped = model.predict(X)
                probs = None
                confidences = np.ones(len(pred_mapped))

            pred_orig_classes = [inv_class_map.get(m, m) for m in pred_mapped]
            pred_risk_names = [RISK_LEVELS[c] if 0 <= c < len(RISK_LEVELS) else f"Risk-{c}" for c in pred_orig_classes]

            output_df = enriched_df.copy()
            output_df["ml_predicted_class"] = pred_orig_classes
            output_df["ml_predicted_risk"] = pred_risk_names
            output_df["ml_confidence"] = [round(float(c), 4) for c in confidences]

            if probs is not None:
                prob_dicts = []
                for row_prob in probs:
                    p_dict = {}
                    for col_idx, p_val in enumerate(row_prob):
                        orig_c = inv_class_map.get(col_idx, col_idx)
                        c_name = RISK_LEVELS[orig_c] if 0 <= orig_c < len(RISK_LEVELS) else f"Class_{orig_c}"
                        p_dict[c_name] = round(float(p_val), 4)
                    prob_dicts.append(p_dict)
                output_df["ml_class_probabilities"] = prob_dicts

            return True, output_df, None

        except Exception as e:
            return False, df, f"Inference execution failed: {str(e)}"
