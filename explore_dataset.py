"""Explore feature descriptions and sample data from the wind dataset."""
import os
import csv
import sys

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATASET_ROOT = r"C:\Users\hitar\.cache\kagglehub\datasets\azizkasimov\wind-turbine-scada-data-for-early-fault-detection\versions\2"

# --- Feature Descriptions for ALL wind farms ---
print("=" * 80)
print("FEATURE DESCRIPTIONS")
print("=" * 80)

for farm_name in ["Wind Farm A", "Wind Farm B", "Wind Farm C"]:
    filepath = os.path.join(DATASET_ROOT, farm_name, "comma_feature_description.csv")
    if os.path.exists(filepath):
        print(f"\n{'='*40}")
        print(f"  {farm_name}")
        print(f"{'='*40}")
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            reader = csv.reader(fh)
            for i, row in enumerate(reader):
                if i < 80:
                    print(f"  {row}")
        print(f"  Total rows shown above.")

# --- Event Info for ALL wind farms ---
print("\n" + "=" * 80)
print("EVENT INFORMATION")
print("=" * 80)

for farm_name in ["Wind Farm A", "Wind Farm B", "Wind Farm C"]:
    filepath = os.path.join(DATASET_ROOT, farm_name, "comma_event_info.csv")
    if os.path.exists(filepath):
        print(f"\n--- {farm_name} ---")
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            reader = csv.reader(fh)
            for i, row in enumerate(reader):
                if i < 25:
                    print(f"  {row}")

# --- Sample Data: Read headers from comma_0.csv in Wind Farm A ---
print("\n" + "=" * 80)
print("SAMPLE DATASET COLUMNS (Wind Farm A, comma_0.csv)")
print("=" * 80)

sample_path = os.path.join(DATASET_ROOT, "Wind Farm A", "datasets", "comma_0.csv")
if os.path.exists(sample_path):
    with open(sample_path, "r", encoding="utf-8", errors="replace") as fh:
        reader = csv.reader(fh)
        for i, row in enumerate(reader):
            if i == 0:
                print(f"  Total Columns: {len(row)}")
                for j, col in enumerate(row):
                    print(f"    [{j:3d}] {col}")
            elif i <= 3:
                print(f"\n  ROW {i} (first 20 values):")
                for j, val in enumerate(row[:20]):
                    print(f"    [{j:3d}] {val}")
            else:
                break

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
