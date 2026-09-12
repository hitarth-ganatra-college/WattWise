import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def train_solar_nbm():
    solar_root = r"C:\Users\hitar\.cache\kagglehub\datasets\anikannal\solar-power-generation-data\versions\1"
    gen_path = os.path.join(solar_root, "Plant_1_Generation_Data.csv")
    weather_path = os.path.join(solar_root, "Plant_1_Weather_Sensor_Data.csv")
    
    if not os.path.exists(gen_path) or not os.path.exists(weather_path):
        print("Solar dataset not found.")
        return

    print("Loading Solar Datasets...")
    df_gen = pd.read_csv(gen_path)
    df_weather = pd.read_csv(weather_path)

    # Convert timestamps to datetime for merging
    df_gen['DATE_TIME'] = pd.to_datetime(df_gen['DATE_TIME'], format='%d-%m-%Y %H:%M')
    df_weather['DATE_TIME'] = pd.to_datetime(df_weather['DATE_TIME'], format='%Y-%m-%d %H:%M:%S')

    # Merge generation and weather sensor data on DATE_TIME
    print("Merging Generation and Weather Telemetry...")
    df = pd.merge(df_gen, df_weather, on='DATE_TIME', how='inner')

    # Filter out nighttime (IRRADIATION == 0) for training expected power during daytime
    daytime_df = df[df['IRRADIATION'] > 0.05].copy()

    # Features and Target
    # Input: IRRADIATION, AMBIENT_TEMPERATURE, MODULE_TEMPERATURE
    # Target: AC_POWER (or converted kW)
    features = ['IRRADIATION', 'AMBIENT_TEMPERATURE', 'MODULE_TEMPERATURE']
    target = 'AC_POWER'

    X = daytime_df[features]
    y = daytime_df[target]

    print(f"Training Solar NBM Model on {len(daytime_df)} daytime observations...")

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=20, max_depth=12, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_val)
    mae = mean_absolute_error(y_val, preds)
    r2 = r2_score(y_val, preds)

    print(f"Solar NBM Model MAE: {mae:.2f} kW")
    print(f"Solar NBM Model R2 Score: {r2:.4f}")

    os.makedirs(config.MODEL_SAVE_DIR, exist_ok=True)
    model_path = os.path.join(config.MODEL_SAVE_DIR, "nbm_solar_ac_power.joblib")
    joblib.dump(model, model_path, compress=3)
    print(f"Saved Solar NBM Model to: {model_path}")

if __name__ == '__main__':
    train_solar_nbm()
