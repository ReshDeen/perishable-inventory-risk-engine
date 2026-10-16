"""
P.I.R.E. Database Management Module
Provides resilient MongoDB Community Server integration with transparent local JSON fallback.
Ensures zero application crashes if MongoDB service is offline or uninstalled.
"""

from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import LOCAL_DB_DIR, MONGODB_COLLECTIONS, MONGODB_DB_NAME, MONGODB_URI


class DatabaseManager:
    """Manages database transactions for products, predictions, recommendations, and audit logs."""

    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        self.uri = uri or MONGODB_URI
        self.db_name = db_name or MONGODB_DB_NAME
        self.client: Optional[pymongo.MongoClient] = None
        self.db = None
        self.is_connected = False
        self.connection_error: Optional[str] = None
        self.storage_mode = "LOCAL_FALLBACK"

        self._initialize_connection()

    def _initialize_connection(self) -> bool:
        """Attempts connection to MongoDB instance with quick 1.5s timeout."""
        try:
            timeout_ms = 5000 if "mongodb+srv" in self.uri else 2000
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=timeout_ms)
            # Verify connectivity via ping
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.is_connected = True
            self.storage_mode = "MONGODB"
            self.connection_error = None
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self.is_connected = False
            self.storage_mode = "LOCAL_FALLBACK"
            is_atlas = "mongodb+srv" in self.uri
            if is_atlas:
                self.connection_error = (
                    "Unable to connect to MongoDB Atlas Cloud Cluster. "
                    "Please verify that: (1) your username and password in .env are correct, and "
                    "(2) Network Access in MongoDB Atlas has 0.0.0.0/0 (Allow Access from Anywhere) enabled. "
                    f"Detail: {str(e)}"
                )
            else:
                self.connection_error = (
                    f"Unable to reach MongoDB at {self.uri}. "
                    "Ensure MongoDB Community Service is started (e.g. `net start MongoDB`). "
                    f"Error detail: {str(e)}"
                )
            self.client = None
            self.db = None
            return False

    def get_status(self) -> Dict[str, Any]:
        """Returns structured connectivity status and storage mode."""
        return {
            "is_connected": self.is_connected,
            "storage_mode": self.storage_mode,
            "target_uri": self.uri,
            "database_name": self.db_name,
            "collections": list(MONGODB_COLLECTIONS.values()),
            "fallback_dir": str(LOCAL_DB_DIR),
            "connection_error": self.connection_error
        }

    # -------------------------------------------------------------
    # Local Fallback Helper Routines
    # -------------------------------------------------------------
    def _save_local_fallback(self, collection_name: str, records: List[Dict[str, Any]]) -> int:
        file_path = LOCAL_DB_DIR / f"{collection_name}.json"
        existing = []
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        existing.extend(records)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, default=str)
        return len(records)

    def _read_local_fallback(self, collection_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        file_path = LOCAL_DB_DIR / f"{collection_name}.json"
        if not file_path.exists():
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data[-limit:]
        except Exception:
            return []

    # -------------------------------------------------------------
    # Core Persistence Operations
    # -------------------------------------------------------------
    def save_predictions(self, records: List[Dict[str, Any]]) -> Tuple[bool, str, int]:
        """Saves batch prediction results to MongoDB or Local Fallback."""
        if not records:
            return False, "No records provided to persist.", 0

        timestamp = datetime.now().isoformat()
        enriched_records = []
        for r in records:
            item = dict(r)
            item["saved_at"] = timestamp
            enriched_records.append(item)

        if self.is_connected and self.db is not None:
            try:
                col = self.db[MONGODB_COLLECTIONS["predictions"]]
                result = col.insert_many(enriched_records)
                count = len(result.inserted_ids)
                self.log_audit("SAVE_PREDICTIONS", f"Inserted {count} prediction records into MongoDB.")
                return True, f"Successfully persisted {count} records to MongoDB collection '{col.name}'.", count
            except Exception as e:
                # Fallback on runtime db write failure
                count = self._save_local_fallback(MONGODB_COLLECTIONS["predictions"], enriched_records)
                return True, f"MongoDB write failed ({e}). Saved {count} records to Local File Fallback.", count
        else:
            count = self._save_local_fallback(MONGODB_COLLECTIONS["predictions"], enriched_records)
            self.log_audit("SAVE_PREDICTIONS_FALLBACK", f"Persisted {count} records to local fallback file.")
            return True, f"MongoDB offline. Successfully persisted {count} records to Local Fallback storage.", count

    def save_recommendations(self, records: List[Dict[str, Any]]) -> Tuple[bool, str, int]:
        """Saves discount recommendations."""
        if not records:
            return False, "No records provided.", 0

        timestamp = datetime.now().isoformat()
        enriched = [dict(r, saved_at=timestamp) for r in records]

        if self.is_connected and self.db is not None:
            try:
                col = self.db[MONGODB_COLLECTIONS["recommendations"]]
                result = col.insert_many(enriched)
                count = len(result.inserted_ids)
                self.log_audit("SAVE_RECOMMENDATIONS", f"Saved {count} discount recommendations to MongoDB.")
                return True, f"Saved {count} recommendations to MongoDB.", count
            except Exception as e:
                count = self._save_local_fallback(MONGODB_COLLECTIONS["recommendations"], enriched)
                return True, f"Saved {count} recommendations to Local Fallback (MongoDB error: {e}).", count
        else:
            count = self._save_local_fallback(MONGODB_COLLECTIONS["recommendations"], enriched)
            self.log_audit("SAVE_RECOMMENDATIONS_FALLBACK", f"Saved {count} recommendations to local storage.")
            return True, f"MongoDB offline. Saved {count} recommendations to Local Fallback storage.", count

    def save_model_metadata(self, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """Stores model training configuration and test evaluation metrics."""
        entry = dict(metadata)
        entry["created_at"] = datetime.now().isoformat()

        if self.is_connected and self.db is not None:
            try:
                col = self.db[MONGODB_COLLECTIONS["model_metadata"]]
                col.insert_one(entry)
                self.log_audit("SAVE_MODEL_METADATA", "Persisted model training metadata to MongoDB.")
                return True, "Model metadata successfully saved to MongoDB."
            except Exception as e:
                self._save_local_fallback(MONGODB_COLLECTIONS["model_metadata"], [entry])
                return True, f"Model metadata saved to Local Fallback (MongoDB error: {e})."
        else:
            self._save_local_fallback(MONGODB_COLLECTIONS["model_metadata"], [entry])
            self.log_audit("SAVE_MODEL_METADATA_FALLBACK", "Saved model metadata to local storage.")
            return True, "MongoDB offline. Model metadata saved to Local Fallback storage."

    def log_audit(self, action: str, details: str) -> None:
        """Appends an event to the audit trail collection."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "storage_mode": self.storage_mode
        }
        if self.is_connected and self.db is not None:
            try:
                self.db[MONGODB_COLLECTIONS["audit_logs"]].insert_one(log_entry)
                return
            except Exception:
                pass
        self._save_local_fallback(MONGODB_COLLECTIONS["audit_logs"], [log_entry])

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent audit logs."""
        if self.is_connected and self.db is not None:
            try:
                col = self.db[MONGODB_COLLECTIONS["audit_logs"]]
                cursor = col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
                return list(cursor)
            except Exception:
                pass
        return self._read_local_fallback(MONGODB_COLLECTIONS["audit_logs"], limit=limit)
