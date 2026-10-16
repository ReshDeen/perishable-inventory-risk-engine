"""
P.I.R.E. Storage Condition Simulation Module ("What-If" Analysis)
Simulates environmental cold-chain shifts without modifying the pristine baseline dataset.
Computes side-by-side risk transitions and financial exposure deltas.
"""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import CATEGORY_STORAGE_TEMPS, RISK_LEVELS
from src.discount_engine import DiscountEngine
from src.prediction import RiskPredictor
from src.risk_engine import RiskEngine


class StorageSimulator:
    """Simulates retail storage variations and compares baseline vs. simulated risk metrics."""

    @classmethod
    def simulate_temperature_change(
        cls,
        baseline_df: pd.DataFrame,
        temp_delta: float = 0.0,
        target_category: str = "All",
        predictor: Optional[RiskPredictor] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Creates a simulated copy with modified storage temperatures and re-evaluates risk.

        Args:
            baseline_df: Original pristine dataframe (unmodified)
            temp_delta: Temperature adjustment in °C (+ for warmer/abuse, - for colder)
            target_category: "All" or a specific category name (e.g. "Dairy")
            predictor: Initialized RiskPredictor instance

        Returns:
            simulated_df: Assessed simulated dataframe
            comparison: Dict containing side-by-side metric deltas
        """
        # 1. Guarantee pristine baseline
        sim_df = baseline_df.copy(deep=True)

        # 2. Modify temperature feature
        if "temp" in sim_df.columns:
            if target_category == "All":
                sim_df["temp"] = sim_df["temp"] + temp_delta
            else:
                mask = sim_df["category"] == target_category
                sim_df.loc[mask, "temp"] = sim_df.loc[mask, "temp"] + temp_delta

        # Round temperatures
        sim_df["temp"] = sim_df["temp"].round(1)

        # 3. Re-run ML Inference
        if predictor is None:
            predictor = RiskPredictor()

        if predictor.is_loaded:
            success, sim_pred_df, _ = predictor.predict(sim_df)
            if not success:
                sim_pred_df = sim_df
        else:
            sim_pred_df = sim_df

        # 4. Re-evaluate Business & Food Safety Rules
        sim_assessed_df = RiskEngine.evaluate_dataframe(sim_pred_df)

        # 5. Re-evaluate Clearance & Financial Risk
        disc_engine = DiscountEngine()
        sim_final_df = disc_engine.generate_recommendations(sim_assessed_df)

        # 6. Calculate Comparison Metrics
        base_fin = disc_engine.calculate_financial_summary(baseline_df)
        sim_fin = disc_engine.calculate_financial_summary(sim_final_df)

        base_dist = baseline_df["final_risk"].value_counts().to_dict() if "final_risk" in baseline_df.columns else {}
        sim_dist = sim_final_df["final_risk"].value_counts().to_dict()

        # Count individual risk escalations or de-escalations
        risk_rank = {lvl: idx for idx, lvl in enumerate(RISK_LEVELS)}
        escalated_count = 0
        deescalated_count = 0

        if "final_risk" in baseline_df.columns:
            for idx in baseline_df.index:
                b_risk = baseline_df.loc[idx, "final_risk"]
                s_risk = sim_final_df.loc[idx, "final_risk"]
                b_val = risk_rank.get(b_risk, 0)
                s_val = risk_rank.get(s_risk, 0)
                if s_val > b_val:
                    escalated_count += 1
                elif s_val < b_val:
                    deescalated_count += 1

        comparison = {
            "temp_delta_applied": temp_delta,
            "target_category": target_category,
            "escalated_items_count": escalated_count,
            "deescalated_items_count": deescalated_count,
            "baseline_financials": base_fin,
            "simulated_financials": sim_fin,
            "value_at_risk_delta": round(sim_fin["total_value_at_risk"] - base_fin["total_value_at_risk"], 2),
            "potential_recovery_delta": round(sim_fin["total_potential_recovery"] - base_fin["total_potential_recovery"], 2),
            "baseline_distribution": base_dist,
            "simulated_distribution": sim_dist,
            "notes": (
                "Simulation updates derived temperature deviation features and reapplies XGBoost inference and business rules. "
                "Expired items remain permanently flagged as expired in compliance with food safety laws."
            )
        }

        return sim_final_df, comparison
