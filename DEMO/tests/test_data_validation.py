"""
Unit and Integration Tests for Data Ingestion, Column Mapping, and Data Validation
"""

import io
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data_loader import DataLoader
from src.data_validation import DataValidator


def test_column_mapping_aliases():
    """Verify alias mapping handles variations like product_id, mrp, mfg_date."""
    raw_columns = ["product_id", "product_name", "category", "stock", "mrp", "mfg_date", "exp_date"]
    mapping, unmapped, ambiguities = DataLoader.detect_column_mappings(raw_columns)

    assert mapping["product_id"] == "prod_id"
    assert mapping["product_name"] == "prod_name"
    assert mapping["stock"] == "quantity"
    assert mapping["mrp"] == "prod_price"
    assert mapping["mfg_date"] == "mf_date"
    assert len(unmapped) == 0


def test_load_csv_from_string():
    """Verify loading from CSV content buffer."""
    csv_data = """prod_id,prod_name,category,quantity,prod_price,temp,mf_date,exp_date
PRD-1,Fresh Milk,Dairy,20,50.0,3.0,2026-10-01,2026-10-08
PRD-2,White Bread,Bakery,15,40.0,20.0,2026-10-05,2026-10-10
"""
    raw_df, std_df, meta = DataLoader.load_file(io.StringIO(csv_data), filename="test.csv")
    assert meta["success"] is True
    assert len(std_df) == 2
    assert "prod_id" in std_df.columns
    assert "prod_price" in std_df.columns


def test_validation_detects_inverted_dates():
    """Verify logical date validation flags when expiry precedes manufacturing."""
    df = pd.DataFrame([{
        "prod_id": "P-101",
        "prod_name": "Inverted Item",
        "category": "Dairy",
        "quantity": 10,
        "prod_price": 50.0,
        "mf_date": "2026-10-20",
        "exp_date": "2026-10-10"  # Earlier than mf_date!
    }])
    is_operable, annotated_df, summary = DataValidator.validate_dataset(df)
    assert summary["invalid_rows"] == 1
    assert "Logical date error" in annotated_df.loc[0, "_validation_issues"][0]


def test_validation_detects_negative_numbers():
    """Verify rejection of negative prices and negative quantities."""
    df = pd.DataFrame([{
        "prod_id": "P-102",
        "prod_name": "Negative Stock",
        "category": "Meat",
        "quantity": -5,
        "prod_price": -20.0,
        "mf_date": "2026-10-01",
        "exp_date": "2026-10-10"
    }])
    is_operable, annotated_df, summary = DataValidator.validate_dataset(df)
    assert summary["invalid_rows"] == 1
    issues_str = "; ".join(annotated_df.loc[0, "_validation_issues"])
    assert "Negative quantity" in issues_str
    assert "Negative price" in issues_str


def test_validation_missing_required_columns():
    """Verify dataset missing essential columns is flagged."""
    df = pd.DataFrame([{
        "prod_id": "P-103",
        "quantity": 10
    }])
    is_operable, annotated_df, summary = DataValidator.validate_dataset(df)
    assert is_operable is False
    assert len(summary["critical_errors"]) > 0
