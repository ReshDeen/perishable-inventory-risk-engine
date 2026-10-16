"""
P.I.R.E. Synthetic Demonstration Dataset Generator
Generates realistic perishable inventory data anchored dynamically to current date.
Contains valid items across all risk levels: Expired, Critical, High, Medium, and Low.
Includes a few documented edge-case rows to showcase data validation capability.
"""

from datetime import datetime, timedelta
from pathlib import Path
import random
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR, CATEGORY_STORAGE_TEMPS


def generate_sample_inventory(
    num_rows: int = 120,
    reference_date: datetime.date = None,
    include_invalid_examples: bool = True
) -> pd.DataFrame:
    """
    Generates synthetic perishable inventory data.
    Clearly designated as synthetic demonstration data.
    """
    if reference_date is None:
        reference_date = datetime.now().date()

    random.seed(42)

    categories_catalog = {
        "Dairy": [
            ("Whole Milk 1L", "Amul / Mother Dairy", (45.0, 75.0), (1.0, 4.0), 7),
            ("Greek Yogurt 400g", "Epigamia", (60.0, 120.0), (1.0, 4.0), 14),
            ("Cheddar Cheese 200g", "Britannia", (120.0, 250.0), (2.0, 6.0), 45),
            ("Paneer (Cottage Cheese) 200g", "Nandini", (80.0, 110.0), (1.0, 4.0), 8),
            ("Fresh Cream 250ml", "Amul", (55.0, 85.0), (2.0, 5.0), 15),
            ("Salted Butter 500g", "Amul", (240.0, 290.0), (2.0, 6.0), 90),
        ],
        "Meat": [
            ("Fresh Chicken Breast 500g", "FreshToHome", (180.0, 260.0), (-2.0, 2.0), 4),
            ("Mutton Curry Cut 500g", "Licious", (450.0, 650.0), (-2.0, 2.0), 3),
            ("Fresh Salmon Fillet 300g", "OceanDelight", (400.0, 700.0), (-2.0, 1.0), 3),
            ("Chicken Sausages 250g", "Zorabian", (150.0, 220.0), (-2.0, 3.0), 10),
            ("Prawns Peeled 250g", "FreshToHome", (280.0, 380.0), (-2.0, 2.0), 3),
        ],
        "Bakery": [
            ("Whole Wheat Bread 400g", "Harvest Gold", (35.0, 55.0), (18.0, 24.0), 5),
            ("Butter Croissant (Pack of 2)", "The Bakehouse", (80.0, 140.0), (18.0, 24.0), 3),
            ("Multi-Grain Bagel", "Artisan Bakery", (60.0, 95.0), (18.0, 24.0), 4),
            ("Chocolate Muffins (Pack of 4)", "English Oven", (90.0, 150.0), (18.0, 24.0), 6),
            ("Vanilla Sponge Cake 350g", "Modern Bakery", (110.0, 180.0), (16.0, 22.0), 7),
        ],
        "Fruits & Vegetables": [
            ("Organic Spinach 250g", "FarmFresh", (25.0, 45.0), (4.0, 8.0), 4),
            ("Ripe Strawberries 200g", "Mahabaleshwar Farms", (90.0, 160.0), (2.0, 6.0), 4),
            ("Button Mushrooms 200g", "Himalayan Fresh", (50.0, 80.0), (3.0, 7.0), 5),
            ("Bell Peppers Tri-color 500g", "Greenhouse Direct", (70.0, 120.0), (5.0, 10.0), 7),
            ("Baby Carrots 250g", "Organic Valley", (40.0, 70.0), (4.0, 8.0), 10),
            ("Fresh Broccoli 500g", "Hill Farms", (60.0, 110.0), (3.0, 7.0), 6),
        ],
        "Beverages": [
            ("Cold-Pressed Orange Juice 300ml", "Raw Pressery", (80.0, 120.0), (2.0, 6.0), 12),
            ("Probiotic Drink (5x65ml)", "Yakult", (75.0, 95.0), (2.0, 8.0), 30),
            ("Fresh Coconut Water 200ml", "Paper Boat", (45.0, 60.0), (4.0, 12.0), 20),
            ("Cold Brew Coffee 250ml", "Sleepy Owl", (90.0, 140.0), (3.0, 8.0), 25),
            ("Almond Milk Unsweetened 1L", "So Good", (220.0, 280.0), (4.0, 15.0), 60),
        ],
        "Packaged Foods": [
            ("Hummus Classic 200g", "Wingreens Farms", (140.0, 190.0), (2.0, 6.0), 21),
            ("Fresh Salsa Dip 200g", "Habit", (110.0, 160.0), (3.0, 8.0), 18),
            ("Tofu Organic 200g", "Health1st", (70.0, 110.0), (2.0, 6.0), 25),
            ("Fresh Pasta Tagliatelle 250g", "Sorrento", (130.0, 210.0), (2.0, 6.0), 14),
            ("Guacamole Fresh 150g", "Holy Moly", (160.0, 240.0), (2.0, 5.0), 10),
        ]
    }

    suppliers = [
        "Metro Logistics Hub - Mumbai",
        "North Cold-Chain Depot - Delhi",
        "South Distribution Hub - Bengaluru",
        "Coastal Agro Terminal - Chennai",
        "Western Agri-Logistics - Pune",
        "Deccan Fresh Hub - Hyderabad"
    ]

    records = []
    prod_counter = 1001

    # Tier distributions to guarantee all risk profiles:
    # 1. Expired (days remaining: -8 to -1)
    # 2. Critical (days remaining: 0 to 1)
    # 3. High (days remaining: 2 to 3)
    # 4. Medium (days remaining: 4 to 7)
    # 5. Low (days remaining: 8 to 45)

    risk_windows = [
        ("EXPIRED", (-8, -1), 18),
        ("CRITICAL", (0, 1), 22),
        ("HIGH", (2, 3), 25),
        ("MEDIUM", (4, 7), 30),
        ("LOW", (8, 35), 35)
    ]

    for risk_label, (min_days, max_days), count in risk_windows:
        for _ in range(count):
            category = random.choice(list(categories_catalog.keys()))
            item_tuple = random.choice(categories_catalog[category])
            item_name, brand, (price_min, price_max), (temp_min, temp_max), nominal_shelf_life = item_tuple

            days_remaining = random.randint(min_days, max_days)
            exp_date = reference_date + timedelta(days=days_remaining)

            # Realistic total shelf life
            total_shelf_life = max(nominal_shelf_life, abs(days_remaining) + random.randint(3, 15))
            mf_date = exp_date - timedelta(days=total_shelf_life)

            # Storage temperature (with occasional temperature abuse)
            ideal_min, ideal_max, _ = CATEGORY_STORAGE_TEMPS.get(category, (2.0, 8.0, 5.0))
            if random.random() < 0.15:
                # 15% probability of temperature abuse (stored too warm)
                storage_temp = round(ideal_max + random.uniform(2.5, 7.0), 1)
            else:
                storage_temp = round(random.uniform(ideal_min, ideal_max), 1)

            price = round(random.uniform(price_min, price_max), 2)
            quantity = random.randint(5, 120)
            supplier = random.choice(suppliers)

            records.append({
                "prod_id": f"PRD-{prod_counter}",
                "prod_name": item_name,
                "prod_brand": brand,
                "supplier_location": supplier,
                "category": category,
                "quantity": quantity,
                "prod_price": price,
                "temp": storage_temp,
                "mf_date": mf_date.strftime("%Y-%m-%d"),
                "exp_date": exp_date.strftime("%Y-%m-%d")
            })
            prod_counter += 1

    # Add 4 intentional edge-case rows to demonstrate validation capabilities
    if include_invalid_examples:
        records.append({
            "prod_id": f"PRD-{prod_counter}",
            "prod_name": "Defective Entry - Inverted Dates",
            "prod_brand": "DemoBrand",
            "supplier_location": suppliers[0],
            "category": "Dairy",
            "quantity": 25,
            "prod_price": 60.0,
            "temp": 3.5,
            "mf_date": (reference_date + timedelta(days=10)).strftime("%Y-%m-%d"),
            "exp_date": reference_date.strftime("%Y-%m-%d")  # Exp before Mf!
        })
        prod_counter += 1

        records.append({
            "prod_id": f"PRD-{prod_counter}",
            "prod_name": "Defective Entry - Negative Quantity",
            "prod_brand": "DemoBrand",
            "supplier_location": suppliers[1],
            "category": "Bakery",
            "quantity": -10,  # Negative qty!
            "prod_price": 45.0,
            "temp": 20.0,
            "mf_date": (reference_date - timedelta(days=10)).strftime("%Y-%m-%d"),
            "exp_date": (reference_date + timedelta(days=5)).strftime("%Y-%m-%d")
        })
        prod_counter += 1

        records.append({
            "prod_id": "",  # Missing ID!
            "prod_name": "Defective Entry - Missing ID",
            "prod_brand": "DemoBrand",
            "supplier_location": suppliers[2],
            "category": "Meat",
            "quantity": 15,
            "prod_price": 250.0,
            "temp": 0.5,
            "mf_date": (reference_date - timedelta(days=5)).strftime("%Y-%m-%d"),
            "exp_date": (reference_date + timedelta(days=2)).strftime("%Y-%m-%d")
        })
        prod_counter += 1

        # Duplicate ID demo
        records.append({
            "prod_id": "PRD-1001",  # Duplicate of first ID!
            "prod_name": "Duplicate ID Example",
            "prod_brand": "DemoBrand",
            "supplier_location": suppliers[3],
            "category": "Beverages",
            "quantity": 30,
            "prod_price": 85.0,
            "temp": 5.0,
            "mf_date": (reference_date - timedelta(days=8)).strftime("%Y-%m-%d"),
            "exp_date": (reference_date + timedelta(days=12)).strftime("%Y-%m-%d")
        })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    out_path = DATA_DIR / "sample_inventory.csv"
    sample_df = generate_sample_inventory()
    sample_df.to_csv(out_path, index=False)
    print(f"Generated sample dataset with {len(sample_df)} rows at {out_path}")
