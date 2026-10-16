"""
Pipeline verification script testing end-to-end flow:
Data Loading -> Validation -> Prediction -> Risk Engine -> Discount Engine -> PDF Generation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.data_loader import DataLoader
from src.data_validation import DataValidator
from src.prediction import RiskPredictor
from src.risk_engine import RiskEngine
from src.discount_engine import DiscountEngine
from src.report_generator import ReportGenerator

if __name__ == "__main__":
    print("1. Testing DataLoader...")
    raw_df, std_df, meta = DataLoader.load_file("data/sample_inventory.csv")
    assert raw_df is not None and not raw_df.empty, "Failed to load CSV"
    print(f"Loaded {len(std_df)} rows. Mappings: {len(meta['column_mapping'])}")

    print("\n2. Testing DataValidator...")
    is_operable, annotated_df, val_summary = DataValidator.validate_dataset(std_df)
    print(f"Operable: {is_operable}, Valid: {val_summary['valid_rows']}, Warning: {val_summary['warning_rows']}, Invalid: {val_summary['invalid_rows']}")

    print("\n3. Testing RiskPredictor (XGBoost)...")
    predictor = RiskPredictor()
    success, pred_df, err = predictor.predict(annotated_df)
    assert success, f"Prediction failed: {err}"
    print(f"Predictions generated for {len(pred_df)} rows. Model loaded successfully.")

    print("\n4. Testing RiskEngine (Business Rules & Safety Guardrail)...")
    assessed_df = RiskEngine.evaluate_dataframe(pred_df)
    expired_cnt = (assessed_df["final_risk"] == "EXPIRED").sum()
    print(f"Assessed risk categories: {assessed_df['final_risk'].value_counts().to_dict()}")
    print(f"Expired count: {expired_cnt}")

    print("\n5. Testing DiscountEngine...")
    disc_engine = DiscountEngine()
    final_df = disc_engine.generate_recommendations(assessed_df)
    fin_summary = disc_engine.calculate_financial_summary(final_df)
    print(f"Financial summary: {fin_summary}")

    # Check food safety rule: No expired product may have >0 discount
    expired_with_discount = final_df[(final_df["is_expired"] == True) & (final_df["recommended_discount_pct"] > 0)]
    assert len(expired_with_discount) == 0, "CRITICAL ERROR: Expired product has positive discount!"
    print("Food safety assertion verified: 0 expired items discounted.")

    print("\n6. Testing ReportGenerator (PDF & CSV)...")
    pdf_bytes = ReportGenerator.generate_pdf_report(
        final_df,
        fin_summary,
        model_metrics=predictor.metadata,
        output_path="reports/test_audit_report.pdf"
    )
    assert len(pdf_bytes) > 0, "PDF generation failed"
    print(f"PDF successfully created: {len(pdf_bytes)} bytes written to reports/test_audit_report.pdf")

    print("\n=== ALL PIPELINE STAGES PASSED SUCCESSFULLY ===")
