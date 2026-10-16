"""
Initial training verification script for P.I.R.E.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.model_training import ModelTrainer

if __name__ == "__main__":
    csv_path = Path("data/sample_inventory.csv")
    if not csv_path.exists():
        print("Dataset not found at data/sample_inventory.csv")
        exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows.")

    trainer = ModelTrainer()
    success, res = trainer.train_model(df)
    print(f"Training Success: {success}")
    if success:
        print("Metrics:", res.get("metrics"))
        print("Model Path:", res.get("model_path"))
        print("Classes:", res.get("classes_present"))
    else:
        print("Error:", res.get("error"))
