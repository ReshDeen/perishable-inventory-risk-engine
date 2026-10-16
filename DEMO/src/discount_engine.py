"""
P.I.R.E. Dynamic Discount Recommendation Engine
Computes transparent, category-governed clearance discounts and inventory risk valuation.
Strict food safety guardrail: Expired and unsafe goods are strictly ineligible for discount/sale.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCOUNT_CONFIG


class DiscountEngine:
    """Calculates clearance markdowns, inventory value-at-risk, and estimated recovery values."""

    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        self.config = DISCOUNT_CONFIG.copy()
        if custom_config:
            self.config.update(custom_config)

    def calculate_item_discount(self, row: pd.Series) -> Dict[str, Any]:
        """
        Calculates markdown and financial exposure metrics for a single inventory item.
        """
        final_risk = str(row.get("final_risk", row.get("rule_urgency", "LOW"))).upper()
        days_rem = float(row.get("days_remaining", 999.0))
        prod_price = max(0.0, float(row.get("prod_price", 0.0) or 0.0))
        quantity = max(0, int(float(row.get("quantity", 0.0) or 0)))
        category = str(row.get("category", "General")).strip()
        is_expired = bool(row.get("is_expired", False)) or (days_rem <= 0) or (final_risk == "EXPIRED")

        total_inventory_cost = round(prod_price * quantity, 2)

        # 1. STRICT SAFETY GUARDRAIL: Expired Products
        if is_expired:
            return {
                "prod_id": row.get("prod_id", "N/A"),
                "prod_name": row.get("prod_name", "N/A"),
                "category": category,
                "quantity": quantity,
                "original_price": prod_price,
                "recommended_discount_pct": 0.0,
                "discount_amount": 0.0,
                "recommended_selling_price": 0.0,
                "eligible_quantity": 0,
                "is_eligible_for_sale": False,
                "inventory_value_at_risk": total_inventory_cost,
                "estimated_recoverable_value": 0.0,
                "explanation": "CRITICAL FOOD SAFETY VIOLATION: Item is expired. Strictly ineligible for discount or sale. Full stock value is at risk as total write-off."
            }

        # 2. Determine base discount factor by risk level
        risk_factors = self.config.get("risk_discount_factors", {})
        base_discount = risk_factors.get(final_risk, 0.0)

        # If days remaining is very close to zero, apply slight acceleration
        if days_rem <= 1.0 and final_risk in ["CRITICAL", "HIGH"]:
            base_discount = max(base_discount, 0.50)

        # 3. Apply category cap
        cat_caps = self.config.get("category_max_discounts", {})
        cat_cap = cat_caps.get(category, cat_caps.get("General", 0.50))
        capped_discount = min(base_discount, cat_cap)

        # 4. Enforce global min and max boundaries
        min_disc = self.config.get("min_discount", 0.0)
        max_disc = self.config.get("max_discount", 0.70)
        final_discount = max(min_disc, min(max_disc, capped_discount))

        final_discount_pct = round(final_discount * 100.0, 1)

        # 5. Pricing and revenue calculations
        discount_amount = round(prod_price * (final_discount_pct / 100.0), 2)
        selling_price = round(max(0.0, prod_price - discount_amount), 2)

        # Eligible units
        is_discounted = final_discount_pct > 0.0
        eligible_qty = quantity if is_discounted else 0

        # Inventory Value at Risk: Total value tied in items facing expiry threat (MEDIUM, HIGH, CRITICAL)
        if final_risk in ["MEDIUM", "HIGH", "CRITICAL"]:
            value_at_risk = total_inventory_cost
        else:
            value_at_risk = 0.0

        # Potential Recoverable Value: Estimated gross recovery if eligible quantity clears at markdown
        # (Labeled as an estimate, not a revenue guarantee)
        est_recoverable = round(eligible_qty * selling_price, 2) if is_discounted else 0.0

        # Explanation
        if is_discounted:
            explanation = (
                f"Recommended {final_discount_pct}% markdown for {final_risk} risk. "
                f"Governed by {category} clearance cap ({round(cat_cap*100)}%). "
                f"Clearance pricing of ₹{selling_price:.2f} aims to accelerate sell-through before expiry."
            )
        else:
            explanation = "Item has healthy shelf-life and low risk profile. Standard retail price maintained."

        return {
            "prod_id": row.get("prod_id", "N/A"),
            "prod_name": row.get("prod_name", "N/A"),
            "category": category,
            "quantity": quantity,
            "original_price": prod_price,
            "recommended_discount_pct": final_discount_pct,
            "discount_amount": discount_amount,
            "recommended_selling_price": selling_price,
            "eligible_quantity": eligible_qty,
            "is_eligible_for_sale": True,
            "inventory_value_at_risk": value_at_risk,
            "estimated_recoverable_value": est_recoverable,
            "explanation": explanation
        }

    def generate_recommendations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes a full assessed inventory DataFrame and produces discount recommendations.
        """
        records = [self.calculate_item_discount(row) for _, row in df.iterrows()]
        rec_df = pd.DataFrame(records, index=df.index)

        # Merge new columns into original dataframe
        output_df = df.copy()
        for col in [
            "recommended_discount_pct",
            "discount_amount",
            "recommended_selling_price",
            "eligible_quantity",
            "is_eligible_for_sale",
            "inventory_value_at_risk",
            "estimated_recoverable_value",
            "discount_explanation"
        ]:
            if col == "discount_explanation":
                output_df[col] = rec_df["explanation"]
            else:
                output_df[col] = rec_df[col]

        return output_df

    @staticmethod
    def calculate_financial_summary(rec_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates aggregate portfolio financial risk and estimated recovery figures.
        """
        if rec_df.empty:
            return {
                "total_inventory_cost": 0.0,
                "total_value_at_risk": 0.0,
                "total_potential_recovery": 0.0,
                "expired_writeoff_loss": 0.0,
                "discount_eligible_items_count": 0
            }

        cost = (rec_df["prod_price"] * rec_df["quantity"]).sum() if "prod_price" in rec_df.columns and "quantity" in rec_df.columns else 0.0
        risk_val = rec_df["inventory_value_at_risk"].sum() if "inventory_value_at_risk" in rec_df.columns else 0.0
        recov_val = rec_df["estimated_recoverable_value"].sum() if "estimated_recoverable_value" in rec_df.columns else 0.0

        if "is_eligible_for_sale" in rec_df.columns:
            expired_mask = rec_df["is_eligible_for_sale"] == False
        elif "is_expired" in rec_df.columns:
            expired_mask = rec_df["is_expired"] == True
        elif "final_risk" in rec_df.columns:
            expired_mask = rec_df["final_risk"] == "EXPIRED"
        else:
            expired_mask = pd.Series(False, index=rec_df.index)

        if "prod_price" in rec_df.columns and "quantity" in rec_df.columns and expired_mask.any():
            expired_loss = (rec_df.loc[expired_mask, "prod_price"] * rec_df.loc[expired_mask, "quantity"]).sum()
        else:
            expired_loss = 0.0

        eligible_count = (rec_df["recommended_discount_pct"] > 0).sum() if "recommended_discount_pct" in rec_df.columns else 0

        return {
            "total_inventory_cost": round(float(cost), 2),
            "total_value_at_risk": round(float(risk_val), 2),
            "total_potential_recovery": round(float(recov_val), 2),
            "expired_writeoff_loss": round(float(expired_loss), 2),
            "discount_eligible_items_count": int(eligible_count)
        }
