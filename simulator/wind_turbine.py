import pandas as pd
import os
import math
from .base_asset import BaseAsset
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class WindTurbine(BaseAsset):
    def __init__(self, asset_id, region='Temperate', dataset_csv_path=None, wind_farm=None, custom_params=None):
        wind_farm = wind_farm or config.DEFAULT_WIND_FARM
        super().__init__(asset_id, 'wind_turbine', region, config.WIND_TURBINE_CAPACITY_KW, custom_params)
        
        if dataset_csv_path is None:
            datasets_dir = os.path.join(config.DATASET_ROOT, wind_farm, 'datasets')
            if os.path.exists(datasets_dir):
                files = [f for f in os.listdir(datasets_dir) if f.startswith('comma_') and f.endswith('.csv')]
                if files:
                    dataset_csv_path = os.path.join(datasets_dir, files[0])
                    
        self.dataset_csv_path = dataset_csv_path
        self._data_iterator = None
        self._csv_file_handle = None
        self._prev_temps = {}  # For thermal inertia EMA filtering

    def _init_data_stream(self):
        if self.dataset_csv_path and os.path.exists(self.dataset_csv_path):
            self._data_iterator = pd.read_csv(self.dataset_csv_path, chunksize=1)
        else:
            raise FileNotFoundError(f"Dataset CSV not found: {self.dataset_csv_path}")

    def _map_row_to_telemetry(self, row: pd.Series) -> dict:
        def nan_to_none(val):
            return None if pd.isna(val) else val

        data = {
            'ambient_temp': nan_to_none(row.get('sensor_0_avg')),
            'wind_direction': nan_to_none(row.get('sensor_1_avg')),
            'wind_speed': nan_to_none(row.get('wind_speed_3_avg')),
            'wind_speed_max': nan_to_none(row.get('wind_speed_3_max')),
            'wind_speed_min': nan_to_none(row.get('wind_speed_3_min')),
            'wind_speed_std': nan_to_none(row.get('wind_speed_3_std')),
            'pitch_angle': nan_to_none(row.get('sensor_5_avg')),
            'pitch_angle_std': nan_to_none(row.get('sensor_5_std')),
            'gearbox_bearing_temp': nan_to_none(row.get('sensor_11_avg')),
            'gearbox_oil_temp': nan_to_none(row.get('sensor_12_avg')),
            'generator_bearing_de_temp': nan_to_none(row.get('sensor_13_avg')),
            'generator_bearing_nde_temp': nan_to_none(row.get('sensor_14_avg')),
            'generator_stator_temp_1': nan_to_none(row.get('sensor_15_avg')),
            'generator_stator_temp_2': nan_to_none(row.get('sensor_16_avg')),
            'generator_stator_temp_3': nan_to_none(row.get('sensor_17_avg')),
            'generator_rpm': nan_to_none(row.get('sensor_18_avg')),
            'generator_rpm_std': nan_to_none(row.get('sensor_18_std')),
            'rotor_rpm': nan_to_none(row.get('sensor_52_avg')),
            'rotor_rpm_std': nan_to_none(row.get('sensor_52_std')),
            'current_phase_1': nan_to_none(row.get('sensor_23_avg')),
            'current_phase_2': nan_to_none(row.get('sensor_24_avg')),
            'current_phase_3': nan_to_none(row.get('sensor_25_avg')),
            'grid_frequency': nan_to_none(row.get('sensor_26_avg')),
            'active_power': nan_to_none(row.get('power_29_avg')),
            'active_power_std': nan_to_none(row.get('power_29_std')),
            'grid_power': nan_to_none(row.get('power_30_avg')),
            'reactive_power': nan_to_none(row.get('reactive_power_27_avg')),
            'transformer_temp_l1': nan_to_none(row.get('sensor_38_avg')),
            'transformer_temp_l2': nan_to_none(row.get('sensor_39_avg')),
            'transformer_temp_l3': nan_to_none(row.get('sensor_40_avg')),
            'hydraulic_oil_temp': nan_to_none(row.get('sensor_41_avg')),
            'nacelle_temp': nan_to_none(row.get('sensor_43_avg')),
            'nacelle_direction': nan_to_none(row.get('sensor_42_avg')),
            'status_type_id': int(row.get('status_type_id', 0)) if not pd.isna(row.get('status_type_id')) else 0,
            'original_timestamp': str(row.get('time_stamp')),
            'train_test': str(row.get('train_test'))
        }
        
        # Apply regional offset and Thermal Inertia EMA smoothing (alpha = 0.25 -> 30 min lag)
        alpha = 0.25
        temp_keys = [k for k in data.keys() if 'temp' in k]
        for k in temp_keys:
            if data[k] is not None:
                val = data[k] + self.temp_offset
                if k in self._prev_temps:
                    val = alpha * val + (1 - alpha) * self._prev_temps[k]
                self._prev_temps[k] = val
                data[k] = round(val, 2)
                
        return data

    def tick(self) -> bool:
        self.check_for_commands()
        if self._data_iterator is None:
            self._init_data_stream()
            
        try:
            chunk = next(self._data_iterator)
        except StopIteration:
            return False
            
        row = chunk.iloc[0]
        data = self._map_row_to_telemetry(row)
        
        data = self.apply_overrides(data)
        self.emit_telemetry(data)
        super().tick()
        
        return True

    def close(self):
        self._data_iterator = None
