import time
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from .base_asset import BaseAsset
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class FleetManager:
    def __init__(self, mongo_uri=None, db_name=None):
        self.assets: dict[str, BaseAsset] = {}
        self.mongo_uri = mongo_uri or config.MONGO_URI
        self.db_name = db_name or config.DB_NAME
        self._running = False
        self._client = None

    def _get_db(self):
        if self._client is None:
            self._client = MongoClient(self.mongo_uri)
        return self._client[self.db_name]

    def add_asset(self, asset: BaseAsset):
        self.assets[asset.asset_id] = asset
        asset.register_asset()
        print(f"  [Fleet] Added {asset.asset_type} '{asset.asset_id}' ({asset.region})")

    def remove_asset(self, asset_id: str):
        if asset_id in self.assets:
            del self.assets[asset_id]
            db = self._get_db()
            db[config.COLLECTION_ASSETS].update_one(
                {'asset_id': asset_id},
                {'$set': {'status': 'removed'}}
            )
            print(f"  [Fleet] Removed '{asset_id}'")

    def get_fleet_status(self) -> list[dict]:
        return [
            {
                'asset_id': asset.asset_id,
                'asset_type': asset.asset_type,
                'region': asset.region,
                'is_running': asset.is_running,
                'tick_count': asset._tick_count
            }
            for asset in self.assets.values()
        ]

    def send_command(self, asset_id: str, action: str, parameters: dict = None):
        db = self._get_db()
        command = {
            'asset_id': asset_id,
            'action': action,
            'parameters': parameters or {},
            'status': 'pending',
            'created_at': datetime.now(timezone.utc)
        }
        db[config.COLLECTION_COMMANDS].insert_one(command)

    def send_command_to_all(self, action: str, parameters: dict = None):
        for asset_id in self.assets:
            self.send_command(asset_id, action, parameters)

    def _discover_new_assets(self):
        """Poll MongoDB for assets with status='pending' and create simulator objects."""
        from .wind_turbine import WindTurbine
        from .solar_panel import SolarPanel

        db = self._get_db()
        collection = db[config.COLLECTION_ASSETS]
        
        pending = list(collection.find({'status': 'pending'}))
        for doc in pending:
            asset_id = doc['asset_id']
            if asset_id in self.assets:
                # Already running — just mark it active
                collection.update_one({'_id': doc['_id']}, {'$set': {'status': 'active'}})
                continue

            asset_type = doc.get('asset_type', 'wind_turbine')
            region = doc.get('region', 'Temperate')
            custom_params = doc.get('custom_params', {})

            try:
                if asset_type == 'wind_turbine':
                    # Pick a CSV file: use specified one or auto-pick
                    csv_path = doc.get('dataset_csv_path')
                    if not csv_path:
                        datasets_dir = os.path.join(config.DATASET_ROOT, config.DEFAULT_WIND_FARM, 'datasets')
                        csv_files = sorted([
                            f for f in os.listdir(datasets_dir)
                            if f.startswith('comma_') and f.endswith('.csv')
                        ])
                        if csv_files:
                            # Round-robin: pick based on how many wind turbines exist
                            wt_count = sum(1 for a in self.assets.values() if a.asset_type == 'wind_turbine')
                            csv_path = os.path.join(datasets_dir, csv_files[wt_count % len(csv_files)])

                    asset = WindTurbine(
                        asset_id=asset_id,
                        region=region,
                        dataset_csv_path=csv_path,
                        custom_params=custom_params
                    )

                elif asset_type == 'solar_panel':
                    latitude = custom_params.get('latitude', 28.6)
                    asset = SolarPanel(
                        asset_id=asset_id,
                        region=region,
                        latitude=latitude,
                        custom_params=custom_params
                    )
                else:
                    print(f"  [Fleet] Unknown asset type: {asset_type}")
                    collection.update_one({'_id': doc['_id']}, {'$set': {'status': 'error', 'error': f'Unknown type: {asset_type}'}})
                    continue

                # Apply Initial Health Fault Condition if specified
                initial_fault = custom_params.get('initial_fault')
                if initial_fault == 'overheated_gearbox':
                    asset.manual_overrides = {'gearbox_bearing_temp': 25.0, 'gearbox_oil_temp': 20.0}
                    print(f"  [Fleet] Latched Initial Fault: Overheated Gearbox on '{asset_id}'")
                elif initial_fault == 'critical_generator':
                    asset.manual_overrides = {'generator_bearing_de_temp': 40.0}
                    print(f"  [Fleet] Latched Initial Fault: Critical Generator Bearing on '{asset_id}'")
                elif initial_fault == 'diode_fault':
                    if hasattr(asset, 'has_diode_fault'):
                        asset.has_diode_fault = True
                        asset.diode_fault_loss = 0.33
                    print(f"  [Fleet] Latched Initial Fault: Blown Diode on '{asset_id}'")
                elif initial_fault == 'heavy_soiling':
                    if hasattr(asset, 'soiling_factor'):
                        asset.soiling_factor = 0.70
                    print(f"  [Fleet] Latched Initial Fault: Heavy Soiling (0.70) on '{asset_id}'")

                self.add_asset(asset)
                collection.update_one({'_id': doc['_id']}, {'$set': {'status': 'active'}})
                print(f"  [Fleet] 🆕 Discovered and activated '{asset_id}'")

            except Exception as e:
                print(f"  [Fleet] Error creating '{asset_id}': {e}")
                collection.update_one({'_id': doc['_id']}, {'$set': {'status': 'error', 'error': str(e)}})

    def run(self, max_ticks: int = None, tick_interval: float = None):
        if tick_interval is None:
            tick_interval = config.TICK_INTERVAL_SECONDS

        self._running = True
        ticks = 0

        try:
            while self._running:
                if max_ticks is not None and ticks >= max_ticks:
                    break

                # Check for new assets every 5 ticks
                if ticks % 5 == 0:
                    self._discover_new_assets()

                # Remove finished assets
                finished = []
                for asset_id, asset in self.assets.items():
                    if not asset.tick():
                        finished.append(asset_id)

                for aid in finished:
                    print(f"  [Fleet] Asset '{aid}' data stream ended.")
                    del self.assets[aid]

                ticks += 1
                time.sleep(tick_interval)

        except KeyboardInterrupt:
            print("\n[Fleet] Simulation interrupted by user.")
        finally:
            self._running = False
            print(f"[Fleet] Simulation stopped after {ticks} ticks.")

    def stop(self):
        self._running = False
