"""
Unit and Integration Tests for Risk Engine and Food Safety Rules
"""

from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.risk_engine import RiskEngine


def test_food_safety_override_expired_product():
    """Verify expired products are ALWAYS marked EXPIRED, even if ML predicted LOW."""
    ref_date = datetime(2026, 10, 16)
    row = pd.Series({
        "prod_id": "P-999",
        "prod_name": "Old Milk",
        "category": "Dairy",
        "quantity": 10,
        "prod_price": 60.0,
        "temp": 3.0,
        "mf_date": "2026-10-01",
        "exp_date": "2026-10-15"  # 1 day overdue relative to ref_date
    })

    # Deliberately feed ML prediction as 'LOW' to verify safety override
    eval_res = RiskEngine.evaluate_item_rules(
        row,
        ml_prediction="LOW",
        ml_confidence=0.99,
        reference_date=ref_date
    )

    assert eval_res["is_expired"] is True
    assert eval_res["final_risk"] == "EXPIRED"
    assert "REMOVE IMMEDIATELY" in eval_res["recommended_action"]


def test_critical_and_high_risk_thresholds():
    """Verify items expiring in 1 day are CRITICAL and 2-3 days are HIGH."""
    ref_date = datetime(2026, 10, 16)

    # 1 day remaining -> CRITICAL
    crit_row = pd.Series({
        "prod_id": "P-101",
        "category": "Bakery",
        "quantity": 5,
        "prod_price": 50.0,
        "temp": 20.0,
        "exp_date": (ref_date + timedelta(days=1)).strftime("%Y-%m-%d")
    })
    res_crit = RiskEngine.evaluate_item_rules(crit_row, reference_date=ref_date)
    assert res_crit["rule_urgency"] == "CRITICAL"

    # 3 days remaining -> HIGH
    high_row = pd.Series({
        "prod_id": "P-102",
        "category": "Meat",
        "quantity": 5,
        "prod_price": 200.0,
        "temp": 0.0,
        "exp_date": (ref_date + timedelta(days=3)).strftime("%Y-%m-%d")
    })
    res_high = RiskEngine.evaluate_item_rules(high_row, reference_date=ref_date)
    assert res_high["rule_urgency"] == "HIGH"


def test_temperature_anomaly_escalation():
    """Verify severe temperature violation escalates risk."""
    ref_date = datetime(2026, 10, 16)
    warm_dairy_row = pd.Series({
        "prod_id": "P-103",
        "category": "Dairy",  # Max recommended temp is 4°C
        "quantity": 10,
        "prod_price": 60.0,
        "temp": 12.0,  # 8°C above max!
        "exp_date": (ref_date + timedelta(days=15)).strftime("%Y-%m-%d")
    })

    res = RiskEngine.evaluate_item_rules(warm_dairy_row, ml_prediction="LOW", reference_date=ref_date)
    assert res["final_risk"] == "HIGH"
    assert any("Temperature abuse" in r for r in res["flag_reasons"])
