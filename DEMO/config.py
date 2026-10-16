"""
P.I.R.E. (Perishable Inventory Risk Evaluation)
Configuration and Business Constants Module
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOCAL_DB_DIR = BASE_DIR / "local_fallback_db"

for directory in [DATA_DIR, MODELS_DIR, REPORTS_DIR, LOCAL_DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Load .env file if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception:
        pass

# Environment Variables & Cloud Secrets Support
_mongo_uri_default = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
try:
    import streamlit as st
    MONGODB_URI = st.secrets.get("MONGODB_URI", _mongo_uri_default)
except Exception:
    MONGODB_URI = _mongo_uri_default

MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "pire_inventory")
APP_ENV = os.getenv("APP_ENV", "development")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
DEFAULT_RANDOM_SEED = int(os.getenv("DEFAULT_RANDOM_SEED", 42))

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "தமிழ் (Tamil)",
    "hi": "हिन्दी (Hindi)"
}

# Risk Categories
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL", "EXPIRED"]

# Risk Thresholds (Days until Expiry)
EXPIRY_THRESHOLDS = {
    "EXPIRED": 0,      # <= 0 days: Product is already past expiry
    "CRITICAL": 1,     # <= 1 day: Immediate clearance needed if safe
    "HIGH": 3,         # <= 3 days: Imminent expiry risk
    "MEDIUM": 7,       # <= 7 days: Moderate expiry window
    # > 7 days is LOW
}

# Category Storage Temperature Norms (Degrees Celsius)
# (Min acceptable temp, Max acceptable temp, Default storage temp)
CATEGORY_STORAGE_TEMPS = {
    "Dairy": (1.0, 4.0, 3.0),
    "Meat": (-2.0, 2.0, 0.0),
    "Bakery": (15.0, 24.0, 20.0),
    "Fruits & Vegetables": (4.0, 10.0, 7.0),
    "Beverages": (2.0, 12.0, 6.0),
    "Packaged Foods": (15.0, 25.0, 20.0),
    "General": (4.0, 20.0, 10.0)
}

# Column Mapping Aliases for Ingestion
COLUMN_ALIASES = {
    "prod_id": ["prod_id", "product_id", "item_id", "id", "sku", "productid"],
    "prod_name": ["prod_name", "product_name", "item_name", "name", "title", "productname"],
    "prod_brand": ["prod_brand", "product_brand", "brand", "manufacturer", "make"],
    "supplier_location": ["supplier_location", "supplier", "location", "origin", "distributor_location"],
    "category": ["category", "product_category", "cat", "dept", "department"],
    "quantity": ["quantity", "qty", "stock", "inventory_count", "units", "quantity_in_stock"],
    "prod_price": ["prod_price", "price", "product_price", "unit_price", "mrp", "retail_price"],
    "temp": ["temp", "temperature", "storage_temp", "storage_temperature", "current_temp"],
    "mf_date": ["mf_date", "manufacturing_date", "mfg_date", "mfg", "production_date", "packaged_date"],
    "exp_date": ["exp_date", "expiry_date", "exp", "expiration_date", "best_before", "use_by"]
}

# Required columns for core pipeline
REQUIRED_COLUMNS = ["prod_id", "prod_name", "category", "quantity", "prod_price", "mf_date", "exp_date"]

# Discount Recommendation Configuration
DISCOUNT_CONFIG = {
    "min_discount": 0.0,
    "max_discount": 0.70,  # Never discount more than 70%
    "risk_discount_factors": {
        "EXPIRED": 0.0,    # Strictly 0% - NEVER sell expired food!
        "CRITICAL": 0.50,  # 50% clearance discount
        "HIGH": 0.35,      # 35% discount
        "MEDIUM": 0.15,    # 15% promotional discount
        "LOW": 0.0         # 0% standard price
    },
    # Cap discount by category to protect brand value / margins
    "category_max_discounts": {
        "Dairy": 0.60,
        "Meat": 0.60,
        "Bakery": 0.70,
        "Fruits & Vegetables": 0.50,
        "Beverages": 0.40,
        "Packaged Foods": 0.45,
        "General": 0.50
    }
}

# MongoDB Collections
MONGODB_COLLECTIONS = {
    "products": "products",
    "predictions": "predictions",
    "recommendations": "discount_recommendations",
    "audit_logs": "audit_logs",
    "model_metadata": "model_metadata"
}
