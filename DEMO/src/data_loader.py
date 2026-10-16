"""
P.I.R.E. Data Ingestion and Column Mapping Module
Supports CSV and Excel files, standardizes column aliases, and preserves raw data.
"""

from io import BytesIO, StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import COLUMN_ALIASES, REQUIRED_COLUMNS


class DataLoader:
    """Handles loading and column schema normalization for perishable inventory datasets."""

    @staticmethod
    def detect_column_mappings(df_columns: List[str]) -> Tuple[Dict[str, str], List[str], List[str]]:
        """
        Maps source DataFrame columns to standardized P.I.R.E. schema fields.

        Returns:
            mapping: dict {source_column: standard_column}
            unmapped_columns: list of columns that didn't match known aliases
            ambiguous_columns: list of warnings where multiple source columns matched the same standard field
        """
        mapping: Dict[str, str] = {}
        standard_to_source: Dict[str, List[str]] = {}
        unmapped_columns: List[str] = []

        # Normalize column names: strip whitespace, lowercase, replace spaces/hyphens with underscores
        cleaned_to_orig = {col: str(col).strip() for col in df_columns}

        for orig_col in df_columns:
            normalized_name = str(orig_col).strip().lower().replace(" ", "_").replace("-", "_")
            matched_standard = None

            for std_field, aliases in COLUMN_ALIASES.items():
                aliases_normalized = [a.lower().replace(" ", "_").replace("-", "_") for a in aliases]
                if normalized_name in aliases_normalized:
                    matched_standard = std_field
                    break

            if matched_standard:
                mapping[orig_col] = matched_standard
                standard_to_source.setdefault(matched_standard, []).append(orig_col)
            else:
                unmapped_columns.append(orig_col)

        ambiguous_warnings: List[str] = []
        for std_field, source_cols in standard_to_source.items():
            if len(source_cols) > 1:
                ambiguous_warnings.append(
                    f"Ambiguity detected: Multiple columns {source_cols} map to '{std_field}'. Using '{source_cols[0]}'."
                )

        return mapping, unmapped_columns, ambiguous_warnings

    @classmethod
    def load_file(
        cls, file_source: Union[str, Path, BytesIO, StringIO], filename: Optional[str] = None
    ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Dict[str, any]]:
        """
        Loads CSV or Excel file and returns:
            raw_df: Original unmodified dataframe
            standardized_df: Dataframe with mapped column names
            meta: Metadata including mapping results, warnings, file type
        """
        meta = {
            "success": False,
            "filename": filename or (str(file_source) if isinstance(file_source, (str, Path)) else "uploaded_file"),
            "file_type": None,
            "total_rows": 0,
            "total_columns": 0,
            "column_mapping": {},
            "missing_required": [],
            "unmapped_columns": [],
            "warnings": [],
            "error": None
        }

        # Determine file type
        fname = meta["filename"].lower()
        try:
            if fname.endswith(".csv") or isinstance(file_source, StringIO):
                meta["file_type"] = "CSV"
                raw_df = pd.read_csv(file_source)
            elif fname.endswith((".xlsx", ".xls")):
                meta["file_type"] = "Excel"
                raw_df = pd.read_excel(file_source)
            else:
                meta["error"] = f"Unsupported file type. Supported formats: .csv, .xlsx, .xls. Found: '{fname}'"
                return None, None, meta
        except Exception as e:
            meta["error"] = f"Failed to parse file: {str(e)}"
            return None, None, meta

        if raw_df.empty:
            meta["error"] = "The uploaded file is empty (0 rows)."
            return raw_df, None, meta

        meta["total_rows"] = len(raw_df)
        meta["total_columns"] = len(raw_df.columns)

        mapping, unmapped, ambiguities = cls.detect_column_mappings(list(raw_df.columns))
        meta["column_mapping"] = mapping
        meta["unmapped_columns"] = unmapped
        meta["warnings"].extend(ambiguities)

        # Create standardized copy
        # Inverse mapping: only pick the first occurrence if multiple map to the same
        rename_dict = {}
        assigned_stds = set()
        for src, std in mapping.items():
            if std not in assigned_stds:
                rename_dict[src] = std
                assigned_stds.add(std)

        standardized_df = raw_df.rename(columns=rename_dict).copy()

        # Check required columns
        present_cols = set(standardized_df.columns)
        missing_req = [col for col in REQUIRED_COLUMNS if col not in present_cols]
        meta["missing_required"] = missing_req
        if missing_req:
            meta["warnings"].append(
                f"Missing required columns for full risk evaluation: {missing_req}"
            )

        meta["success"] = True
        return raw_df, standardized_df, meta
