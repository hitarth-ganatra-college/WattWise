import time
from datetime import datetime, timezone
from pymongo import MongoClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class BaseAsset:
    def __init__(self, asset_id: str, asset_type: str, region: str = 'Temperate', capacity_kw: float = 0, custom_params: dict = None):
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.region = region
        self.capacity_kw = capacity_kw
        
        regional_mods = config.REGIONAL_MODIFIERS.get(region, {})
        self.temp_offset = regional_mods.get('temp_offset', 0)
        self.dust_factor = regional_mods.get('dust_factor', 0)
        
        self.manual_overrides = {}
        self.custom_params = custom_params or {}
        self.is_running = False
        self._tick_count = 0
        self._db = None

    def _get_db(self):
        if self._db is None:
            client = MongoClient(config.MONGO_URI)
            self._db = client[config.DB_NAME]
        return self._db

    def check_for_commands(self):
        db = self._get_db()
        collection = db[config.COLLECTION_COMMANDS]
        
        pending_commands = collection.find({
            'asset_id': self.asset_id,
            'status': 'pending'
        })
        
        for cmd in pending_commands:
            action = cmd.get('action')
            parameters = cmd.get('parameters', {})
            
            if action == 'override':
                self.manual_overrides.update(parameters)
            elif action == 'inject_fault':
                self.manual_overrides.update(parameters)
            elif action == 'clear_overrides':
                self.manual_overrides = {}
            elif action == 'stop':
                self.is_running = False
                
            collection.update_one(
                {'_id': cmd['_id']},
                {'$set': {
                    'status': 'executed',
                    'executed_at': datetime.now(timezone.utc)
                }}
            )

    def apply_overrides(self, data: dict) -> dict:
        for k, v in self.manual_overrides.items():
            if k in data:
                data[k] = data[k] + v if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(data[k], (int, float)) else v
            else:
                data[k] = v
        return data

    def emit_telemetry(self, sensor_data: dict):
        db = self._get_db()
        collection = db[config.COLLECTION_TELEMETRY]
        
        telemetry = {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type,
            'region': self.region,
            'capacity_kw': self.capacity_kw,
            'timestamp': datetime.now(timezone.utc),
            'tick_count': self._tick_count,
        }
        # Flatten sensor data into the top-level document
        telemetry.update(sensor_data)
        
        collection.insert_one(telemetry)
        print(f"[{self.asset_id}] Telemetry emitted (Tick {self._tick_count})")

    def register_asset(self):
        db = self._get_db()
        collection = db[config.COLLECTION_ASSETS]
        
        asset_doc = {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type,
            'region': self.region,
            'capacity_kw': self.capacity_kw,
            'registered_at': datetime.now(timezone.utc),
            'status': 'active'
        }
        
        collection.update_one(
            {'asset_id': self.asset_id},
            {'$set': asset_doc},
            upsert=True
        )

    def tick(self) -> bool:
        self._tick_count += 1
        return True
