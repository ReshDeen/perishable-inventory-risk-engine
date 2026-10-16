"""
P.I.R.E. Data Validation Module
Performs comprehensive sanity and business-rule validation on inventory records.
Never silently discards data; flags specific issues row by row with recommendations.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import REQUIRED_COLUMNS, CATEGORY_STORAGE_TEMPS


class DataValidator:
    """Validates inventory dataset rows against schema, domain integrity, and logical rules."""

    @staticmethod
    def validate_dataset(df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, Dict[str, Any]]:
        """
        Validates the incoming DataFrame.

        Returns:
            is_valid: bool (True if dataset has at least 1 valid record and required columns)
            annotated_df: DataFrame with additional columns:
                - `_validation_status`: 'VALID', 'WARNING', or 'INVALID'
                - `_validation_issues`: list of strings describing any issues
            summary: Dict containing counts, errors, warnings, and affected row indices
        """
        summary = {
            "total_rows": len(df) if df is not None else 0,
            "valid_rows": 0,
            "warning_rows": 0,
            "invalid_rows": 0,
            "critical_errors": [],
            "warnings": [],
            "row_issues": [],
            "is_operable": False
        }

        if df is None or df.empty:
            summary["critical_errors"].append("The dataset is empty. Cannot perform evaluation.")
            return False, pd.DataFrame(), summary

        # Check required columns
        missing_req = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_req:
            summary["critical_errors"].append(
                f"Dataset is missing required columns: {missing_req}. "
                f"Required schema: {REQUIRED_COLUMNS}"
            )
            return False, df.copy(), summary

        annotated_df = df.copy()
        annotated_df["_validation_status"] = "VALID"
        annotated_df["_validation_issues"] = [[] for _ in range(len(annotated_df))]

        # Track duplicates
        seen_ids = set()
        duplicate_ids = set()
        for idx, val in annotated_df["prod_id"].items():
            s_val = str(val).strip() if pd.notna(val) else ""
            if not s_val or s_val.lower() == "nan":
                continue
            if s_val in seen_ids:
                duplicate_ids.add(s_val)
            seen_ids.add(s_val)

        row_issues_list = []

        for idx, row in annotated_df.iterrows():
            issues = []
            is_fatal = False

            # 1. Product Identifier and Name
            prod_id_val = row.get("prod_id")
            s_prod_id = str(prod_id_val).strip() if pd.notna(prod_id_val) else ""
            if not s_prod_id or s_prod_id.lower() in ("nan", "none", "null", ""):
                issues.append("Missing product ID")
                is_fatal = True
            elif s_prod_id in duplicate_ids:
                issues.append(f"Duplicate product ID '{s_prod_id}' found in dataset")
                # Warning rather than fatal so user can inspect both

            prod_name_val = row.get("prod_name")
            s_prod_name = str(prod_name_val).strip() if pd.notna(prod_name_val) else ""
            if not s_prod_name or s_prod_name.lower() in ("nan", "none", "null", ""):
                issues.append("Missing product name")
                is_fatal = True

            # 2. Numeric Validations: Quantity
            qty_val = row.get("quantity")
            try:
                qty_num = float(qty_val)
                if np.isnan(qty_num):
                    issues.append("Quantity is missing/NaN")
                    is_fatal = True
                elif qty_num < 0:
                    issues.append(f"Negative quantity ({qty_num}) is not permissible")
                    is_fatal = True
            except (ValueError, TypeError):
                issues.append(f"Non-numeric quantity value '{qty_val}'")
                is_fatal = True

            # 3. Numeric Validations: Price
            price_val = row.get("prod_price")
            try:
                price_num = float(price_val)
                if np.isnan(price_num):
                    issues.append("Price is missing/NaN")
                    is_fatal = True
                elif price_num < 0:
                    issues.append(f"Negative price ({price_num}) is not permissible")
                    is_fatal = True
            except (ValueError, TypeError):
                issues.append(f"Non-numeric price value '{price_val}'")
                is_fatal = True

            # 4. Dates Validation
            mf_parsed = None
            exp_parsed = None

            try:
                mf_parsed = pd.to_datetime(row.get("mf_date"), errors="coerce")
                if pd.isna(mf_parsed):
                    issues.append(f"Invalid manufacturing date format: '{row.get('mf_date')}'")
                    is_fatal = True
            except Exception:
                issues.append(f"Unparseable manufacturing date: '{row.get('mf_date')}'")
                is_fatal = True

            try:
                exp_parsed = pd.to_datetime(row.get("exp_date"), errors="coerce")
                if pd.isna(exp_parsed):
                    issues.append(f"Invalid expiry date format: '{row.get('exp_date')}'")
                    is_fatal = True
            except Exception:
                issues.append(f"Unparseable expiry date: '{row.get('exp_date')}'")
                is_fatal = True

            # Logical date check: exp_date must be >= mf_date
            if mf_parsed is not None and exp_parsed is not None and pd.notna(mf_parsed) and pd.notna(exp_parsed):
                if exp_parsed < mf_parsed:
                    issues.append(
                        f"Logical date error: Expiry date ({exp_parsed.strftime('%Y-%m-%d')}) "
                        f"is earlier than Manufacturing date ({mf_parsed.strftime('%Y-%m-%d')})"
                    )
                    is_fatal = True

            # 5. Storage Temperature (Warning if missing or extreme)
            temp_val = row.get("temp")
            if "temp" in annotated_df.columns:
                try:
                    temp_num = float(temp_val)
                    if np.isnan(temp_num):
                        issues.append("Missing storage temperature (default category temp will be imputed)")
                    elif temp_num < -30 or temp_num > 50:
                        issues.append(f"Extreme storage temperature reading ({temp_num}°C)")
                except (ValueError, TypeError):
                    issues.append(f"Non-numeric temperature value '{temp_val}'")

            # Determine row status
            if is_fatal:
                status = "INVALID"
                summary["invalid_rows"] += 1
            elif issues:
                status = "WARNING"
                summary["warning_rows"] += 1
            else:
                status = "VALID"
                summary["valid_rows"] += 1

            annotated_df.at[idx, "_validation_status"] = status
            annotated_df.at[idx, "_validation_issues"] = issues

            if issues:
                row_issues_list.append({
                    "row_index": int(idx),
                    "prod_id": s_prod_id or f"Row {idx}",
                    "prod_name": s_prod_name or "N/A",
                    "status": status,
                    "issues": "; ".join(issues)
                })

        summary["row_issues"] = row_issues_list
        summary["is_operable"] = summary["valid_rows"] + summary["warning_rows"] > 0

        return summary["is_operable"], annotated_df, summary
