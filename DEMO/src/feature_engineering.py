"""
P.I.R.E. Feature Engineering Pipeline Module
Extracts domain-specific shelf-life and storage features from raw inventory records.
Supports consistent feature generation for both training and real-time inference.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import CATEGORY_STORAGE_TEMPS, EXPIRY_THRESHOLDS, RISK_LEVELS


class FeatureEngineer:
    """Derives domain features from inventory attributes and constructs ML training matrices."""

    NUMERICAL_FEATURES = [
        "days_until_expiry",
        "product_age_days",
        "total_shelf_life",
        "shelf_life_ratio",
        "quantity",
        "prod_price",
        "temp",
        "temp_deviation"
    ]

    CATEGORICAL_FEATURES = ["category"]

    def __init__(self, reference_date: Optional[Union[datetime, str]] = None):
        if reference_date is None:
            self.reference_date = pd.Timestamp.now().normalize()
        elif isinstance(reference_date, str):
            self.reference_date = pd.to_datetime(reference_date).normalize()
        else:
            self.reference_date = pd.to_datetime(reference_date).normalize()

    def derive_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates time-delta, shelf-life ratio, and temperature deviation features.
        Preserves original columns and returns an enriched DataFrame copy.
        """
        enriched = df.copy()

        # Parse dates
        mf_dates = pd.to_datetime(enriched["mf_date"], errors="coerce")
        exp_dates = pd.to_datetime(enriched["exp_date"], errors="coerce")

        ref_ts = self.reference_date

        # 1. Temporal features
        enriched["days_until_expiry"] = (exp_dates - ref_ts).dt.total_seconds() / (24 * 3600)
        enriched["product_age_days"] = (ref_ts - mf_dates).dt.total_seconds() / (24 * 3600)
        enriched["total_shelf_life"] = (exp_dates - mf_dates).dt.total_seconds() / (24 * 3600)

        # Avoid divide-by-zero or negative shelf-life
        total_life_safe = enriched["total_shelf_life"].clip(lower=1.0)
        enriched["shelf_life_ratio"] = (enriched["days_until_expiry"] / total_life_safe).clip(lower=-1.0, upper=2.0)

        # 2. Temperature deviation from category standard
        def calc_temp_dev(row):
            cat = str(row.get("category", "General")).strip()
            temp_val = row.get("temp", np.nan)
            if pd.isna(temp_val):
                return 0.0

            try:
                t = float(temp_val)
                min_t, max_t, _ = CATEGORY_STORAGE_TEMPS.get(cat, CATEGORY_STORAGE_TEMPS["General"])
                if t > max_t:
                    return t - max_t  # Warm abuse (excess heat)
                elif t < min_t:
                    return min_t - t  # Cold abuse (excess freezing)
                return 0.0
            except (ValueError, TypeError):
                return 0.0

        enriched["temp_deviation"] = enriched.apply(calc_temp_dev, axis=1)

        # 3. Clean numeric columns
        for num_col in ["quantity", "prod_price", "temp"]:
            if num_col in enriched.columns:
                enriched[num_col] = pd.to_numeric(enriched[num_col], errors="coerce")

        return enriched

    @staticmethod
    def generate_proxy_labels(df: pd.DataFrame) -> pd.Series:
        """
        Generates rule-based proxy teaching labels for datasets lacking verified ground truth.
        Labels:
            0: LOW (> 7 days)
            1: MEDIUM (4 - 7 days)
            2: HIGH (2 - 3 days)
            3: CRITICAL (0 - 1 days)
            4: EXPIRED (<= -1 days or expired)

        Note: These represent a rule-based training reference, not physical spoilage ground truth.
        """
        days = df["days_until_expiry"]

        labels = pd.Series(index=df.index, dtype=int)
        labels[days <= EXPIRY_THRESHOLDS["EXPIRED"]] = 4  # EXPIRED
        labels[(days > EXPIRY_THRESHOLDS["EXPIRED"]) & (days <= EXPIRY_THRESHOLDS["CRITICAL"])] = 3  # CRITICAL
        labels[(days > EXPIRY_THRESHOLDS["CRITICAL"]) & (days <= EXPIRY_THRESHOLDS["HIGH"])] = 2  # HIGH
        labels[(days > EXPIRY_THRESHOLDS["HIGH"]) & (days <= EXPIRY_THRESHOLDS["MEDIUM"])] = 1  # MEDIUM
        labels[days > EXPIRY_THRESHOLDS["MEDIUM"]] = 0  # LOW

        # Fallback for any NaN
        labels = labels.fillna(0).astype(int)
        return labels

    @classmethod
    def build_preprocessor(cls) -> ColumnTransformer:
        """Constructs an sklearn ColumnTransformer with imputers, scalers, and encoders."""
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])

        cat_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_transformer, cls.NUMERICAL_FEATURES),
                ("cat", cat_transformer, cls.CATEGORICAL_FEATURES)
            ],
            remainder="drop"
        )
        return preprocessor
