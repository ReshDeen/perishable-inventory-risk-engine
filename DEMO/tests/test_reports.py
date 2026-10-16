"""
Unit and Integration Tests for Reports (PDF, CSV) and Database Fallback
"""

from pathlib import Path
import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.database import DatabaseManager
from src.discount_engine import DiscountEngine
from src.report_generator import ReportGenerator
from src.risk_engine import RiskEngine


def test_pdf_report_generation(tmp_path):
    """Verify that ReportLab compiles a valid, non-empty PDF document."""
    df = pd.DataFrame([{
        "prod_id": "P-001",
        "prod_name": "Test Yogurt",
        "category": "Dairy",
        "quantity": 10,
        "prod_price": 50.0,
        "temp": 3.0,
        "mf_date": "2026-10-01",
        "exp_date": "2026-10-18",
        "days_remaining": 2.0,
        "final_risk": "HIGH",
        "is_expired": False,
        "recommended_discount_pct": 35.0,
        "recommended_selling_price": 32.50,
        "inventory_value_at_risk": 500.0,
        "estimated_recoverable_value": 325.0
    }])

    disc_engine = DiscountEngine()
    fin_summary = disc_engine.calculate_financial_summary(df)

    pdf_out = tmp_path / "test_report.pdf"
    pdf_bytes = ReportGenerator.generate_pdf_report(
        df=df,
        financial_summary=fin_summary,
        model_metrics={"metrics": {"accuracy": 0.95, "f1_score": 0.94}},
        output_path=pdf_out
    )

    assert len(pdf_bytes) > 1000
    assert pdf_out.exists()
    assert pdf_out.stat().st_size > 1000


def test_csv_export_bytes():
    """Verify valid CSV byte stream generation."""
    df = pd.DataFrame([{"id": 1, "name": "Apple"}])
    csv_bytes = ReportGenerator.generate_csv_bytes(df)
    assert b"id,name" in csv_bytes
    assert b"Apple" in csv_bytes


def test_database_offline_graceful_fallback(tmp_path, monkeypatch):
    """Verify DatabaseManager falls back gracefully when MongoDB is offline."""
    # Point to an invalid port where MongoDB is guaranteed offline
    fake_uri = "mongodb://localhost:29999/"
    mgr = DatabaseManager(uri=fake_uri)

    status = mgr.get_status()
    assert status["is_connected"] is False
    assert status["storage_mode"] == "LOCAL_FALLBACK"

    # Verify saving prediction in fallback mode succeeds
    test_records = [{"prod_id": "P-TEST", "final_risk": "MEDIUM"}]
    success, msg, count = mgr.save_predictions(test_records)
    assert success is True
    assert count == 1
    assert "Local Fallback" in msg
