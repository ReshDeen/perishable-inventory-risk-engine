"""
P.I.R.E. Model Training and Evaluation Pipeline
Trains an authentic XGBoost multi-class classifier to predict expiry risk tiers.
Persists model artifacts, preprocessor, and honest evaluation metrics.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
import xgboost as xgb

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DEFAULT_RANDOM_SEED, MODELS_DIR, RISK_LEVELS
from src.feature_engineering import FeatureEngineer


class ModelTrainer:
    """Manages training, evaluation, and serialization of the XGBoost risk model."""

    MODEL_FILENAME = "pire_xgboost_model.joblib"
    PREPROCESSOR_FILENAME = "pire_preprocessor.joblib"
    METADATA_FILENAME = "model_metadata.json"

    def __init__(self, random_seed: int = DEFAULT_RANDOM_SEED):
        self.random_seed = random_seed
        self.fe = FeatureEngineer()

    def train_model(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None,
        test_size: float = 0.2,
        model_save_dir: Path = MODELS_DIR
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Trains the XGBoost classifier on input dataframe.

        Returns:
            success: bool
            results: dict with training metadata, metrics, warnings, and artifact paths
        """
        results = {
            "success": False,
            "trained_at": datetime.now().isoformat(),
            "train_samples": 0,
            "test_samples": 0,
            "classes_present": [],
            "metrics": {},
            "confusion_matrix": None,
            "classification_report": None,
            "warnings": [],
            "error": None,
            "model_path": None,
            "preprocessor_path": None,
            "metadata_path": None
        }

        try:
            # 1. Feature Engineering
            enriched_df = self.fe.derive_features(df)

            # 2. Target Label Strategy
            if target_column and target_column in enriched_df.columns:
                y = enriched_df[target_column]
                target_source = f"Provided column: {target_column}"
            else:
                y = FeatureEngineer.generate_proxy_labels(enriched_df)
                target_source = "Generated proxy rule-based labels (Rule-based training baseline)"
                results["warnings"].append(
                    "Trained on proxy rule-based labels. Serves as educational baseline and does not imply physical lab verification."
                )

            results["target_source"] = target_source

            # Check number of samples
            n_samples = len(enriched_df)
            if n_samples < 10:
                results["error"] = f"Dataset too small for model training (requires at least 10 valid records, found {n_samples})."
                return False, results

            unique_classes = np.unique(y)
            results["classes_present"] = [RISK_LEVELS[c] if c < len(RISK_LEVELS) else str(c) for c in unique_classes]

            if len(unique_classes) < 2:
                results["error"] = (
                    f"Dataset only contains a single class: {results['classes_present']}. "
                    "Cannot train a discriminative multi-class classifier without diverse risk samples."
                )
                return False, results

            # 3. Preprocessing
            preprocessor = FeatureEngineer.build_preprocessor()

            # 4. Train-Test Split with stratification check
            class_counts = pd.Series(y).value_counts()
            min_class_count = class_counts.min()

            can_stratify = (min_class_count >= 2) and (test_size * n_samples >= len(unique_classes))
            if not can_stratify:
                results["warnings"].append(
                    "Stratified split disabled due to low count in some classes. Used standard random split."
                )

            X_train_raw, X_test_raw, y_train, y_test = train_test_split(
                enriched_df,
                y,
                test_size=test_size,
                random_state=self.random_seed,
                stratify=y if can_stratify else None
            )

            # Fit preprocessor on train only to prevent leakage
            X_train = preprocessor.fit_transform(X_train_raw)
            X_test = preprocessor.transform(X_test_raw)

            results["train_samples"] = len(X_train)
            results["test_samples"] = len(X_test)

            # 5. XGBoost Model Initialization and Fitting
            # Map classes to dense 0..K-1 if needed
            class_map = {orig: idx for idx, orig in enumerate(sorted(unique_classes))}
            inv_class_map = {idx: orig for orig, idx in class_map.items()}

            y_train_mapped = np.array([class_map[val] for val in y_train])
            y_test_mapped = np.array([class_map[val] for val in y_test])

            num_classes = len(unique_classes)

            if num_classes == 2:
                objective = "binary:logistic"
                eval_metric = "logloss"
            else:
                objective = "multi:softprob"
                eval_metric = "mlogloss"

            xgb_clf = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.08,
                subsample=0.85,
                colsample_bytree=0.85,
                objective=objective,
                eval_metric=eval_metric,
                random_state=self.random_seed
            )

            xgb_clf.fit(X_train, y_train_mapped)

            # 6. Evaluation on Test Set
            y_pred_mapped = xgb_clf.predict(X_test)
            y_pred = np.array([inv_class_map[val] for val in y_pred_mapped])

            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
            rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
            f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

            results["metrics"] = {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4)
            }

            results["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
            target_names = [RISK_LEVELS[c] if c < len(RISK_LEVELS) else str(c) for c in sorted(unique_classes)]
            results["classification_report"] = classification_report(
                y_test, y_pred, target_names=target_names, output_dict=True, zero_division=0
            )

            # 7. Persistence
            model_save_dir = Path(model_save_dir)
            model_save_dir.mkdir(parents=True, exist_ok=True)

            model_path = model_save_dir / self.MODEL_FILENAME
            prep_path = model_save_dir / self.PREPROCESSOR_FILENAME
            meta_path = model_save_dir / self.METADATA_FILENAME

            bundle = {
                "model": xgb_clf,
                "class_map": class_map,
                "inv_class_map": inv_class_map,
                "num_classes": num_classes,
                "feature_names": preprocessor.get_feature_names_out().tolist()
            }

            joblib.dump(bundle, model_path)
            joblib.dump(preprocessor, prep_path)

            results["model_path"] = str(model_path)
            results["preprocessor_path"] = str(prep_path)
            results["metadata_path"] = str(meta_path)
            results["success"] = True

            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

            return True, results

        except Exception as e:
            results["error"] = f"Training failed with exception: {str(e)}"
            return False, results
