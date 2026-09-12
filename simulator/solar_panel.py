import math
import random
from datetime import datetime, timedelta
from .base_asset import BaseAsset
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class SolarPanel(BaseAsset):
    def __init__(self, asset_id, region='Temperate', latitude=28.6, custom_params=None):
        super().__init__(asset_id, 'solar_panel', region, config.SOLAR_PANEL_CAPACITY_KW, custom_params)
        self.latitude = latitude
        self.sim_time = datetime(2024, 1, 1, 6, 0)
        self.soiling_factor = 1.0
        self.soiling_rate = self.custom_params.get('soiling_rate', 0.001)
        self.inverter_efficiency = self.custom_params.get('inverter_efficiency', 0.96)
        self.has_diode_fault = False
        self.diode_fault_loss = 0.0
        self.cloud_cover = 0.0
        self._weather_change_counter = 0

    def _calculate_solar_irradiance(self) -> float:
        day_of_year = self.sim_time.timetuple().tm_yday
        declination = 23.45 * math.sin(2 * math.pi * (284 + day_of_year) / 365)
        hour_angle = 15 * (self.sim_time.hour + self.sim_time.minute / 60.0 - 12)
        
        lat_rad = math.radians(self.latitude)
        decl_rad = math.radians(declination)
        ha_rad = math.radians(hour_angle)
        
        sin_alt = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad)
        solar_altitude = math.asin(sin_alt)
        
        if solar_altitude <= 0:
            return 0.0
            
        clear_sky_irradiance = 1000 * math.sin(solar_altitude)
        irradiance = clear_sky_irradiance * (1 - 0.75 * self.cloud_cover)
        irradiance += random.uniform(-10, 10)
        
        return max(0.0, irradiance)

    def _calculate_panel_temperature(self, irradiance: float, ambient_temp: float) -> float:
        noct = 45.0
        panel_temp = ambient_temp + (noct - 20) * irradiance / 800.0
        return panel_temp

    def _calculate_power_output(self, irradiance: float, panel_temp: float) -> float:
        efficiency_at_stc = 0.20
        temp_coefficient = -0.004
        temp_factor = 1 + temp_coefficient * (panel_temp - 25)
        
        panel_area = self.capacity_kw / efficiency_at_stc
        
        raw_power = irradiance * panel_area * efficiency_at_stc * temp_factor
        raw_power *= self.soiling_factor
        
        if self.has_diode_fault:
            raw_power *= (1 - self.diode_fault_loss)
            
        raw_power *= self.inverter_efficiency
        
        max_power_w = self.capacity_kw * 1000.0
        clamped_power = max(0.0, min(raw_power, max_power_w))
        
        return clamped_power / 1000.0

    def _update_weather(self):
        self._weather_change_counter += 1
        if self._weather_change_counter >= 6:
            self._weather_change_counter = 0
            self.cloud_cover += random.uniform(-0.1, 0.1)
            self.cloud_cover = max(0.0, min(1.0, self.cloud_cover))
            
        if random.random() < 0.01:
            self.cloud_cover = random.uniform(0.5, 1.0)

    def _update_soiling(self):
        if self.dust_factor > 0:
            self.soiling_factor = max(0.7, self.soiling_factor - self.soiling_rate * self.dust_factor)
        else:
            self.soiling_factor = max(0.85, self.soiling_factor - self.soiling_rate)

    def tick(self) -> bool:
        self.sim_time += timedelta(minutes=10)
        self._update_weather()
        self._update_soiling()
        
        day_of_year = self.sim_time.timetuple().tm_yday
        day_angle = 2 * math.pi * (day_of_year - 1) / 365.0
        hour_angle = 2 * math.pi * (self.sim_time.hour - 12) / 24.0
        
        ambient_temp = 25 + 10 * math.sin(day_angle) + 5 * math.sin(hour_angle) + self.temp_offset + random.uniform(-1, 1)
        
        irradiance = self._calculate_solar_irradiance()
        panel_temp = self._calculate_panel_temperature(irradiance, ambient_temp)
        power_output = self._calculate_power_output(irradiance, panel_temp)
        
        # Calculate expected power (clean panels, no faults) for anomaly comparison
        efficiency_at_stc = 0.20
        temp_coefficient = -0.004
        temp_factor = 1 + temp_coefficient * (panel_temp - 25)
        panel_area = self.capacity_kw / efficiency_at_stc
        expected_power_w = irradiance * panel_area * efficiency_at_stc * temp_factor * self.inverter_efficiency
        expected_power_kw = max(0.0, min(expected_power_w / 1000.0, self.capacity_kw))
        
        sensor_data = {
            'ambient_temp': ambient_temp,
            'solar_irradiance': irradiance,
            'panel_temp': panel_temp,
            'power_output_kw': power_output,
            'expected_power_kw': expected_power_kw,
            'soiling_factor': self.soiling_factor,
            'inverter_efficiency': self.inverter_efficiency,
            'has_diode_fault': self.has_diode_fault,
            'diode_fault_loss': self.diode_fault_loss,
            'cloud_cover': self.cloud_cover
        }
        
        self.check_for_commands()
        
        if 'inject_diode_fault' in self.manual_overrides:
            self.has_diode_fault = True
            self.diode_fault_loss = self.manual_overrides.get('diode_fault_loss', 0.33)
            
        if 'clean_panels' in self.manual_overrides:
            self.soiling_factor = 1.0
            if 'clean_panels' in self.manual_overrides:
                del self.manual_overrides['clean_panels']
                
        sensor_data = self.apply_overrides(sensor_data)
        self.emit_telemetry(sensor_data)
        super().tick()
        
        return True
