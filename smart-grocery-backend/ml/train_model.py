from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier


def main():
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "data" / "synthetic_inventory_data.csv"
    model_dir = base_dir / "model"
    model_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_dataset.py first.")

    df = pd.read_csv(data_path)

    feature_cols = [
        "quantity",
        "consumption_rate",
        "days_to_expiry",
        "price_per_unit",
        "stock_level",
    ]

    X = df[feature_cols]
    y = df["risk_label"]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="mlogloss",
        random_state=42,
    )

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    model_path = model_dir / "risk_model.pkl"
    encoder_path = model_dir / "label_encoder.pkl"

    joblib.dump(model, model_path)
    joblib.dump(label_encoder, encoder_path)

    print(f"Model saved to {model_path}")
    print(f"Encoder saved to {encoder_path}")
    print(f"Validation accuracy: {score:.4f}")


if __name__ == "__main__":
    main()
