import json
import sys
from pathlib import Path

import joblib
import pandas as pd


ACTIONS = {
    "High Risk": "Apply Discount Immediately",
    "Moderate Risk": "Prioritize Sales and Monitor Daily",
    "Safe": "Maintain Current Inventory Strategy",
}


def fallback_rule(payload):
    days = int(payload.get("daysToExpiry", 0))
    stock = float(payload.get("quantity", 0))
    consumption = float(payload.get("consumptionRate", 0))

    if days <= 2 or (stock > 120 and consumption < 5):
        label = "High Risk"
        confidence = 0.94
    elif days <= 6 or (stock > 80 and consumption < 8):
        label = "Moderate Risk"
        confidence = 0.82
    else:
        label = "Safe"
        confidence = 0.9

    return {
        "riskPrediction": label,
        "confidenceScore": confidence,
        "recommendedAction": ACTIONS[label],
    }


def load_assets(base_dir):
    model_path = base_dir / "model" / "risk_model.pkl"
    encoder_path = base_dir / "model" / "label_encoder.pkl"

    if not model_path.exists() or not encoder_path.exists():
        return None, None

    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    return model, encoder


def predict(payload):
    base_dir = Path(__file__).resolve().parent
    model, encoder = load_assets(base_dir)

    if model is None or encoder is None:
        return fallback_rule(payload)

    features = pd.DataFrame(
        [
            {
                "quantity": float(payload.get("quantity", 0)),
                "consumption_rate": float(payload.get("consumptionRate", 0)),
                "days_to_expiry": int(payload.get("daysToExpiry", 0)),
                "price_per_unit": float(payload.get("pricePerUnit", 0)),
                "stock_level": float(payload.get("quantity", 0)),
            }
        ]
    )

    probabilities = model.predict_proba(features)[0]
    pred_class = model.predict(features)[0]
    label = encoder.inverse_transform([pred_class])[0]
    confidence = float(max(probabilities))

    return {
        "riskPrediction": label,
        "confidenceScore": round(confidence, 2),
        "recommendedAction": ACTIONS.get(label, "Monitor"),
    }


if __name__ == "__main__":
    try:
        payload = json.loads(sys.stdin.read().strip() or "{}")
        result = predict(payload)
        print(json.dumps(result))
    except Exception as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)
