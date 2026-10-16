"""
P.I.R.E. Expiry Risk and Decision Engine
Harmonizes deterministic retail food-safety rules with XGBoost predictive inference.
Guarantees food safety: Expired items are strictly flagged for removal with 0% discount.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import CATEGORY_STORAGE_TEMPS, EXPIRY_THRESHOLDS, RISK_LEVELS


class RiskEngine:
    """Evaluates business rules, temp compliance, and combines with ML predictions."""

    @staticmethod
    def calculate_days_remaining(exp_date_val: Any, reference_date: Optional[datetime] = None) -> float:
        """Calculates days remaining from reference date to expiry date."""
        if reference_date is None:
            ref_ts = pd.Timestamp.now().normalize()
        else:
            ref_ts = pd.to_datetime(reference_date).normalize()

        exp_ts = pd.to_datetime(exp_date_val, errors="coerce")
        if pd.isna(exp_ts):
            return 0.0

        return float((exp_ts - ref_ts).total_seconds() / (24 * 3600))

    @classmethod
    def evaluate_item_rules(
        cls,
        row: pd.Series,
        ml_prediction: Optional[str] = None,
        ml_confidence: Optional[float] = None,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a single inventory item against deterministic food-safety rules and ML output.
        """
        days_rem = cls.calculate_days_remaining(row.get("exp_date"), reference_date)
        category = str(row.get("category", "General")).strip()
        quantity = float(row.get("quantity", 0) or 0)
        temp_val = row.get("temp", np.nan)

        reasons = []

        # 1. Deterministic Rule Urgency
        if days_rem <= EXPIRY_THRESHOLDS["EXPIRED"]:
            rule_urgency = "EXPIRED"
            reasons.append(
                f"Product reached expiry date on {str(row.get('exp_date'))} ({abs(round(days_rem, 1))} days overdue)."
            )
        elif days_rem <= EXPIRY_THRESHOLDS["CRITICAL"]:
            rule_urgency = "CRITICAL"
            reasons.append(f"Extreme expiry proximity: Only {round(days_rem, 1)} day(s) remaining before expiration.")
        elif days_rem <= EXPIRY_THRESHOLDS["HIGH"]:
            rule_urgency = "HIGH"
            reasons.append(f"Imminent expiry: {round(days_rem, 1)} days remaining until expiration.")
        elif days_rem <= EXPIRY_THRESHOLDS["MEDIUM"]:
            rule_urgency = "MEDIUM"
            reasons.append(f"Approaching expiry window: {round(days_rem, 1)} days remaining.")
        else:
            rule_urgency = "LOW"
            reasons.append(f"Healthy shelf-life: {round(days_rem, 1)} days remaining.")

        # 2. Temperature compliance
        temp_violation = False
        if pd.notna(temp_val):
            try:
                t = float(temp_val)
                min_t, max_t, _ = CATEGORY_STORAGE_TEMPS.get(category, CATEGORY_STORAGE_TEMPS["General"])
                if t > max_t:
                    temp_violation = True
                    deg_over = round(t - max_t, 1)
                    reasons.append(
                        f"Temperature abuse: Stored at {t}°C, which is {deg_over}°C above recommended maximum ({max_t}°C) for {category}."
                    )
                elif t < min_t:
                    temp_violation = True
                    deg_under = round(min_t - t, 1)
                    reasons.append(
                        f"Sub-cooling anomaly: Stored at {t}°C, which is {deg_under}°C below recommended minimum ({min_t}°C) for {category}."
                    )
            except (ValueError, TypeError):
                pass

        # 3. Stock volume pressure check
        if days_rem > 0 and days_rem <= 4 and quantity > 40:
            reasons.append(f"High inventory exposure: {int(quantity)} units in stock with narrow sales window.")

        # 4. Mandatory Food Safety Override:
        # If product is physically expired, final category MUST be EXPIRED regardless of ML prediction!
        if rule_urgency == "EXPIRED":
            final_risk = "EXPIRED"
            is_expired = True
            action = "REMOVE IMMEDIATELY FROM SHELF — Condemn for safe retail disposal. Do not sell or discount."
        else:
            is_expired = False
            # If ML is available and reliable, report ML risk or blend with rule urgency
            if ml_prediction and ml_prediction in RISK_LEVELS:
                # If temperature was severely abused, escalate to at least HIGH
                if temp_violation and ml_prediction in ["LOW", "MEDIUM"]:
                    final_risk = "HIGH"
                    reasons.append("Risk escalated to HIGH due to uncorrected temperature violation.")
                else:
                    final_risk = ml_prediction
            else:
                # Fallback to rule urgency if ML is not loaded
                final_risk = rule_urgency

            # Action assignment
            if final_risk == "CRITICAL":
                action = "URGENT CLEARANCE — Apply steep clearance discount and place in front-of-store priority bin."
            elif final_risk == "HIGH":
                action = "PROMOTIONAL MARKDOWN — Apply promotional discount and feature on display endcap."
            elif final_risk == "MEDIUM":
                action = "FIRST-IN FIRST-OUT (FIFO) — Prioritize front-facing placement and monitor daily velocity."
            else:
                action = "STANDARD RETENTION — Retain regular pricing and perform standard shelf-life checks."

        return {
            "days_remaining": round(days_rem, 1),
            "rule_urgency": rule_urgency,
            "final_risk": final_risk,
            "is_expired": is_expired,
            "flag_reasons": reasons,
            "recommended_action": action,
            "ml_predicted_risk": ml_prediction or "N/A",
            "ml_confidence": ml_confidence if ml_confidence is not None else "N/A"
        }

    @classmethod
    def evaluate_dataframe(
        cls,
        df: pd.DataFrame,
        reference_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Processes a full DataFrame and appends consolidated risk assessment columns.
        """
        output_df = df.copy()

        # Check if ML columns exist
        has_ml = "ml_predicted_risk" in output_df.columns

        eval_records = []
        for _, row in output_df.iterrows():
            ml_risk = row.get("ml_predicted_risk") if has_ml else None
            ml_conf = row.get("ml_confidence") if has_ml else None

            res = cls.evaluate_item_rules(
                row,
                ml_prediction=ml_risk,
                ml_confidence=ml_conf,
                reference_date=reference_date
            )
            eval_records.append(res)

        eval_df = pd.DataFrame(eval_records, index=output_df.index)

        # Merge results into output
        for col in eval_df.columns:
            output_df[col] = eval_df[col]

        return output_df
