"""
IoT Simulator Entry Point
=========================
Starts the fleet simulator. Assets are discovered dynamically from MongoDB.

Usage:
    # Start with auto-discovery only (assets created from dashboard):
    python simulator/run_simulation.py

    # Seed 2 wind turbines + 2 solar panels as defaults, then keep discovering:
    python simulator/run_simulation.py --seed-defaults

    # Custom tick settings:
    python simulator/run_simulation.py --seed-defaults --tick-interval 1 --max-ticks 500
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from simulator.fleet_manager import FleetManager
from simulator.wind_turbine import WindTurbine
from simulator.solar_panel import SolarPanel


def seed_default_assets(fleet: FleetManager):
    """Create a default set of assets for quick demo."""
    csv_dir = os.path.join(config.DATASET_ROOT, config.DEFAULT_WIND_FARM, 'datasets')
    csv_files = sorted([
        f for f in os.listdir(csv_dir)
        if f.startswith('comma_') and f.endswith('.csv')
    ]) if os.path.exists(csv_dir) else []

    defaults = [
        WindTurbine(
            asset_id='WT-Temperate-01',
            region='Temperate',
            dataset_csv_path=os.path.join(csv_dir, csv_files[0]) if csv_files else None
        ),
        WindTurbine(
            asset_id='WT-Desert-02',
            region='Desert',
            dataset_csv_path=os.path.join(csv_dir, csv_files[1]) if len(csv_files) > 1 else None
        ),
        SolarPanel(
            asset_id='SP-Desert-01',
            region='Desert',
            latitude=25.0  # Rajasthan/Arizona-like
        ),
        SolarPanel(
            asset_id='SP-Coastal-02',
            region='Coastal',
            latitude=12.9  # Bangalore-like
        ),
    ]

    for asset in defaults:
        fleet.add_asset(asset)


def main():
    parser = argparse.ArgumentParser(description="PdM IoT Fleet Simulator")
    parser.add_argument("--seed-defaults", action="store_true",
                        help="Seed default wind turbines and solar panels before starting")
    parser.add_argument("--max-ticks", type=int, default=None,
                        help="Maximum number of simulation ticks")
    parser.add_argument("--tick-interval", type=float, default=None,
                        help="Seconds between each simulation tick")
    args = parser.parse_args()

    fleet = FleetManager()

    if args.seed_defaults:
        print("=" * 60)
        print("  Seeding default fleet assets...")
        print("=" * 60)
        seed_default_assets(fleet)

    print("=" * 60)
    print("  PdM Fleet Simulator Starting")
    print("=" * 60)
    print(f"  MongoDB:      {config.MONGO_URI}")
    print(f"  Database:     {config.DB_NAME}")
    print(f"  Tick interval: {args.tick_interval or config.TICK_INTERVAL_SECONDS}s")
    print(f"  Max ticks:    {args.max_ticks or 'Infinity'}")
    print(f"  Seed defaults: {'Yes' if args.seed_defaults else 'No (discovery only)'}")
    print()

    if fleet.assets:
        print("  Initial Fleet:")
        for s in fleet.get_fleet_status():
            print(f"    - [{s['asset_id']}] {s['asset_type']} ({s['region']})")
    else:
        print("  No initial assets. Waiting for assets from dashboard...")
        print("  (Create assets in the Dashboard -> Asset Manager tab)")

    print("=" * 60)
    print()

    fleet.run(max_ticks=args.max_ticks, tick_interval=args.tick_interval)


if __name__ == "__main__":
    main()
