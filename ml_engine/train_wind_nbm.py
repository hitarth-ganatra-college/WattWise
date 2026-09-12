import argparse
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def train_nbm(csv_path):
    print(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)

    # Filter to training data and normal operation
    if 'train_test' in df.columns:
        df = df[df['train_test'] == 'train']
    if 'status_type_id' in df.columns:
        df = df[df['status_type_id'] == 0]

    # Map columns to human-readable names
    column_mapping = {
        'sensor_0_avg': 'ambient_temp',
        'wind_speed_3_avg': 'wind_speed',
        'sensor_52_avg': 'rotor_rpm',
        'power_29_avg': 'active_power',
        'sensor_5_avg': 'pitch_angle',
        'sensor_11_avg': 'gearbox_bearing_temp',
        'sensor_12_avg': 'gearbox_oil_temp',
        'sensor_13_avg': 'generator_bearing_de_temp',
        'sensor_14_avg': 'generator_bearing_nde_temp'
    }
    df.rename(columns=column_mapping, inplace=True)

    features = config.WIND_NBM_FEATURES
    targets = config.WIND_NBM_TARGETS

    # Ensure columns exist
    for col in features + targets:
        if col not in df.columns:
            print(f"Warning: Column {col} not found in dataset. Ensure it's mapped correctly.")

    df = df[features + targets].dropna()

    print(f"Training on {len(df)} samples.")

    X = df[features]
    
    os.makedirs(config.MODEL_SAVE_DIR, exist_ok=True)

    for target in targets:
        print(f"\n--- Training NBM for {target} ---")
        y = df[target]

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=20, max_depth=12, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)

        preds = model.predict(X_val)
        mae = mean_absolute_error(y_val, preds)
        r2 = r2_score(y_val, preds)

        print(f"Validation MAE: {mae:.4f}")
        print(f"Validation R2: {r2:.4f}")

        model_path = os.path.join(config.MODEL_SAVE_DIR, f"nbm_{target}.joblib")
        joblib.dump(model, model_path, compress=3)
        print(f"Saved model to {model_path}")

    print("\nTraining summary: All NBM models trained successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train Normal Behavior Models for wind turbines.")
    default_csv = r"C:\Users\hitar\.cache\kagglehub\datasets\azizkasimov\wind-turbine-scada-data-for-early-fault-detection\versions\2\Wind Farm A\datasets\comma_0.csv"
    parser.add_argument('--csv-path', type=str, default=default_csv, help="Path to the training CSV file")
    args = parser.parse_args()

    train_nbm(args.csv_path)
