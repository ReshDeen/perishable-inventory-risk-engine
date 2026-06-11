import random
from pathlib import Path

import pandas as pd


CATEGORIES = ["Vegetables", "Fruits", "Dairy", "Meat", "Bakery", "Seafood"]


def derive_risk(days_to_expiry, stock_level, consumption_rate):
    if days_to_expiry <= 2 or (stock_level > 120 and consumption_rate < 5):
        return "High Risk"
    if days_to_expiry <= 6 or (stock_level > 80 and consumption_rate < 8):
        return "Moderate Risk"
    return "Safe"


def build_record():
    quantity = random.randint(5, 200)
    consumption_rate = round(random.uniform(1.0, 25.0), 2)
    days_to_expiry = random.randint(1, 30)
    price_per_unit = round(random.uniform(10.0, 500.0), 2)
    stock_level = quantity
    category = random.choice(CATEGORIES)

    risk = derive_risk(days_to_expiry, stock_level, consumption_rate)

    return {
        "category": category,
        "quantity": quantity,
        "consumption_rate": consumption_rate,
        "days_to_expiry": days_to_expiry,
        "price_per_unit": price_per_unit,
        "stock_level": stock_level,
        "risk_label": risk,
    }


def main(records=6000):
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    rows = [build_record() for _ in range(records)]
    df = pd.DataFrame(rows)
    output_path = data_dir / "synthetic_inventory_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Dataset generated at {output_path} with {len(df)} rows")


if __name__ == "__main__":
    main()
