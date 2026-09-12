import os

MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'predictive_maintenance'
COLLECTION_TELEMETRY = 'telemetry_live'
COLLECTION_COMMANDS = 'simulation_commands'
COLLECTION_ASSETS = 'assets'
COLLECTION_ANOMALY_SCORES = 'anomaly_scores'
COLLECTION_REPAIR_HISTORY = 'repair_history'
COLLECTION_ALERTS = 'alert_notifications'

# Email Notification & Alert Configs
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
ALERT_RECIPIENT_EMAIL = os.getenv('ALERT_RECIPIENT_EMAIL', 'maintenance-ops@cleanenergypdm.com')
ALERT_COOLDOWN_MINUTES = 15  # Avoid spamming duplicate emails for same asset within 15m
DATASET_ROOT = r'C:\Users\hitar\.cache\kagglehub\datasets\azizkasimov\wind-turbine-scada-data-for-early-fault-detection\versions\2'
DEFAULT_WIND_FARM = 'Wind Farm A'
TICK_INTERVAL_SECONDS = 2
ELECTRICITY_PRICE_PER_KWH = 0.10  # USD
EMERGENCY_REPLACEMENT_COST = 50000
PREVENTIVE_MAINTENANCE_COST = 5000

REGIONAL_MODIFIERS = {
    'Desert': {'temp_offset': 10, 'humidity': 20, 'dust_factor': 1.5, 'wind_factor': 1.1, 'lat': 26.9124, 'lon': 70.9023, 'oem_wind': 'Siemens Gamesa SG 3.4-132', 'oem_solar': 'FirstSolar Series 6 Plus'},
    'Nordic': {'temp_offset': -15, 'humidity': 40, 'dust_factor': 0.2, 'wind_factor': 1.2, 'lat': 62.1983, 'lon': 15.0414, 'oem_wind': 'Vestas V117-4.2MW EnVentus', 'oem_solar': 'REC Alpha Pure-R'},
    'Coastal': {'temp_offset': 2, 'humidity': 80, 'dust_factor': 0.5, 'wind_factor': 1.5, 'lat': 21.6417, 'lon': 69.6293, 'oem_wind': 'MHI Vestas V164 Offshore', 'oem_solar': 'SunPower Maxeon 6'},
    'Temperate': {'temp_offset': 0, 'humidity': 50, 'dust_factor': 1.0, 'wind_factor': 1.0, 'lat': 51.1657, 'lon': 10.4515, 'oem_wind': 'GE 2.8-127 Sierra', 'oem_solar': 'Canadian Solar HiKu7'}
}

# Component Supply Chain Procurement Lead Times (in Days)
PROCUREMENT_LEAD_TIMES = {
    'gearbox_bearing_temp': 60,  # Requires heavy-lift vessel or 500t crane
    'gearbox_oil_temp': 45,
    'generator_bearing_de_temp': 21,
    'generator_bearing_nde_temp': 21,
    'vibration': 30,
    'electrical_imbalance': 14,
    'inverter': 5,
    'diode': 2,
    'power_deficit': 3,
    'soiling': 1  # Washing crew dispatch
}

WIND_SENSOR_MAP = {
    'ambient_temp': 'sensor_0_avg',
    'wind_absolute_direction': 'sensor_1_avg',
    'wind_relative_direction': 'sensor_2_avg',
    'wind_speed': 'wind_speed_3_avg',
    'wind_speed_max': 'wind_speed_3_max',
    'wind_speed_min': 'wind_speed_3_min',
    'wind_speed_std': 'wind_speed_3_std',
    'estimated_windspeed': 'wind_speed_4_avg',
    'pitch_angle': 'sensor_5_avg',
    'pitch_angle_max': 'sensor_5_max',
    'pitch_angle_min': 'sensor_5_min',
    'pitch_angle_std': 'sensor_5_std',
    'hub_controller_temp': 'sensor_6_avg',
    'top_nacelle_controller_temp': 'sensor_7_avg',
    'choke_coils_vcs_temp': 'sensor_8_avg',
    'vcp_board_temp': 'sensor_9_avg',
    'vcs_cooling_water_temp': 'sensor_10_avg',
    'gearbox_bearing_temp': 'sensor_11_avg',
    'gearbox_oil_temp': 'sensor_12_avg',
    'generator_bearing_de_temp': 'sensor_13_avg',
    'generator_bearing_nde_temp': 'sensor_14_avg',
    'generator_stator_winding_phase_1_temp': 'sensor_15_avg',
    'generator_stator_winding_phase_2_temp': 'sensor_16_avg',
    'generator_stator_winding_phase_3_temp': 'sensor_17_avg',
    'generator_rpm': 'sensor_18_avg',
    'generator_rpm_max': 'sensor_18_max',
    'generator_rpm_min': 'sensor_18_min',
    'generator_rpm_std': 'sensor_18_std',
    'split_ring_chamber_temp': 'sensor_19_avg',
    'busbar_section_temp': 'sensor_20_avg',
    'igbt_grid_side_temp': 'sensor_21_avg',
    'phase_displacement': 'sensor_22_avg',
    'current_phase_1': 'sensor_23_avg',
    'current_phase_2': 'sensor_24_avg',
    'current_phase_3': 'sensor_25_avg',
    'grid_frequency': 'sensor_26_avg',
    'capacitive_reactive_power': 'reactive_power_27_avg',
    'capacitive_reactive_power_max': 'reactive_power_27_max',
    'capacitive_reactive_power_min': 'reactive_power_27_min',
    'capacitive_reactive_power_std': 'reactive_power_27_std',
    'inductive_reactive_power': 'reactive_power_28_avg',
    'inductive_reactive_power_max': 'reactive_power_28_max',
    'inductive_reactive_power_min': 'reactive_power_28_min',
    'inductive_reactive_power_std': 'reactive_power_28_std',
    'active_power': 'power_29_avg',
    'active_power_max': 'power_29_max',
    'active_power_min': 'power_29_min',
    'active_power_std': 'power_29_std',
    'grid_power': 'power_30_avg',
    'grid_power_max': 'power_30_max',
    'grid_power_min': 'power_30_min',
    'grid_power_std': 'power_30_std',
    'grid_reactive_power': 'sensor_31_avg',
    'grid_reactive_power_max': 'sensor_31_max',
    'grid_reactive_power_min': 'sensor_31_min',
    'grid_reactive_power_std': 'sensor_31_std',
    'phase_voltage_1': 'sensor_32_avg',
    'phase_voltage_2': 'sensor_33_avg',
    'phase_voltage_3': 'sensor_34_avg',
    'igbt_rotor_side_temp_1': 'sensor_35_avg',
    'igbt_rotor_side_temp_2': 'sensor_36_avg',
    'igbt_rotor_side_temp_3': 'sensor_37_avg',
    'hv_transformer_temp_l1': 'sensor_38_avg',
    'hv_transformer_temp_l2': 'sensor_39_avg',
    'hv_transformer_temp_l3': 'sensor_40_avg',
    'hydraulic_oil_temp': 'sensor_41_avg',
    'nacelle_direction': 'sensor_42_avg',
    'nacelle_temp': 'sensor_43_avg',
    'energy_counter_1': 'sensor_44',
    'energy_counter_2': 'sensor_45',
    'energy_counter_3': 'sensor_46',
    'energy_counter_4': 'sensor_47',
    'energy_counter_5': 'sensor_48',
    'energy_counter_6': 'sensor_49',
    'energy_counter_7': 'sensor_50',
    'energy_counter_8': 'sensor_51',
    'rotor_rpm': 'sensor_52_avg',
    'rotor_rpm_max': 'sensor_52_max',
    'rotor_rpm_min': 'sensor_52_min',
    'rotor_rpm_std': 'sensor_52_std',
    'nose_cone_temp': 'sensor_53_avg',
}

WIND_NBM_FEATURES = ['ambient_temp', 'wind_speed', 'rotor_rpm', 'active_power', 'pitch_angle']
WIND_NBM_TARGETS = ['gearbox_bearing_temp', 'gearbox_oil_temp', 'generator_bearing_de_temp', 'generator_bearing_nde_temp']
SOLAR_PANEL_CAPACITY_KW = 10  # kW per panel
WIND_TURBINE_CAPACITY_KW = 2000  # kW per turbine
MODEL_SAVE_DIR = 'models/'
