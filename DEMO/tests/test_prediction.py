"""
Unit and Integration Tests for XGBoost Model Training and Inference
"""

from pathlib import Path
import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.feature_engineering import FeatureEngineer
from src.model_training import ModelTrainer
from src.prediction import RiskPredictor


def test_feature_engineering_derivation():
    """Verify temporal and temperature delta derivation."""
    df = pd.DataFrame([{
        "prod_id": "P-1",
        "category": "Dairy",
        "quantity": 10,
        "prod_price": 50.0,
        "temp": 8.0,
        "mf_date": "2026-10-01",
        "exp_date": "2026-10-10"
    }])
    fe = FeatureEngineer(reference_date="2026-10-05")
    res = fe.derive_features(df)

    assert "days_until_expiry" in res.columns
    assert "shelf_life_ratio" in res.columns
    assert "temp_deviation" in res.columns
    assert res.loc[0, "days_until_expiry"] == 5.0
    assert res.loc[0, "temp_deviation"] == 4.0  # 8°C - 4°C max


def test_model_training_and_prediction(tmp_path):
    """Verify training pipeline generates valid artifacts and predictor runs."""
    sample_path = Path("data/sample_inventory.csv")
    assert sample_path.exists(), "Sample inventory data must exist"

    df = pd.read_csv(sample_path)
    trainer = ModelTrainer(random_seed=42)
    success, results = trainer.train_model(df, model_save_dir=tmp_path)

    assert success is True
    assert "metrics" in results
    assert results["metrics"]["accuracy"] >= 0.80

    # Test Predictor using the temp trained model
    predictor = RiskPredictor(model_dir=tmp_path)
    assert predictor.is_loaded is True

    p_success, pred_df, p_err = predictor.predict(df.head(10))
    assert p_success is True
    assert "ml_predicted_risk" in pred_df.columns
    assert "ml_confidence" in pred_df.columns
    assert len(pred_df) == 10


def test_training_rejects_single_class(tmp_path):
    """Verify training refuses to train when all rows belong to only 1 risk class."""
    # Create 15 items all expiring in 30 days (LOW risk only)
    single_class_df = pd.DataFrame([{
        "prod_id": f"P-{i}",
        "prod_name": "Long Life Item",
        "category": "Packaged Foods",
        "quantity": 10,
        "prod_price": 50.0,
        "temp": 20.0,
        "mf_date": "2026-09-01",
        "exp_date": "2026-11-20"
    } for i in range(15)])

    trainer = ModelTrainer()
    success, results = trainer.train_model(single_class_df, model_save_dir=tmp_path)
    assert success is False
    assert "single class" in results.get("error", "").lower()
