"""
Unit and Integration Tests for Discount Engine and Financial Valuations
"""

from pathlib import Path
import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.discount_engine import DiscountEngine


def test_zero_discount_on_expired_goods():
    """Verify expired items NEVER receive a discount and have 0 recoverable revenue."""
    engine = DiscountEngine()
    row = pd.Series({
        "prod_id": "P-EXP",
        "prod_name": "Sour Milk",
        "category": "Dairy",
        "quantity": 20,
        "prod_price": 50.0,
        "days_remaining": -2.0,
        "final_risk": "EXPIRED",
        "is_expired": True
    })

    res = engine.calculate_item_discount(row)
    assert res["recommended_discount_pct"] == 0.0
    assert res["discount_amount"] == 0.0
    assert res["recommended_selling_price"] == 0.0
    assert res["eligible_quantity"] == 0
    assert res["is_eligible_for_sale"] is False
    assert res["estimated_recoverable_value"] == 0.0
    assert res["inventory_value_at_risk"] == 1000.0  # 20 * 50 = 1000 full write-off


def test_clearance_discount_calculation():
    """Verify discount percentages and price calculations for valid urgent items."""
    engine = DiscountEngine()
    row = pd.Series({
        "prod_id": "P-CRIT",
        "prod_name": "Artisan Bread",
        "category": "Bakery",
        "quantity": 10,
        "prod_price": 100.0,
        "days_remaining": 1.0,
        "final_risk": "CRITICAL",
        "is_expired": False
    })

    res = engine.calculate_item_discount(row)
    assert res["recommended_discount_pct"] == 50.0
    assert res["discount_amount"] == 50.0
    assert res["recommended_selling_price"] == 50.0
    assert res["eligible_quantity"] == 10
    assert res["is_eligible_for_sale"] is True
    assert res["estimated_recoverable_value"] == 500.0  # 10 * 50 = 500
    assert res["inventory_value_at_risk"] == 1000.0  # 10 * 100 = 1000


def test_category_discount_capping():
    """Verify discount does not exceed category cap."""
    engine = DiscountEngine()
    # Beverages has cap of 40% (0.40) in config
    row = pd.Series({
        "prod_id": "P-BEV",
        "prod_name": "Fresh Juice",
        "category": "Beverages",
        "quantity": 5,
        "prod_price": 80.0,
        "days_remaining": 1.0,
        "final_risk": "CRITICAL",
        "is_expired": False
    })

    res = engine.calculate_item_discount(row)
    assert res["recommended_discount_pct"] <= 40.0
