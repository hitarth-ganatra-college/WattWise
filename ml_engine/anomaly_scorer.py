import os
import time
import joblib
from pymongo import MongoClient

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from business_logic.email_notifier import EmailNotifier
from business_logic.health_index import AssetHealthCalculator
from business_logic.financial_engine import FinancialEngine

class AnomalyScorer:
    def __init__(self, mongo_uri=None, db_name=None):
        uri = mongo_uri or getattr(config, 'MONGO_URI', 'mongodb://localhost:27017/')
        db = db_name or getattr(config, 'DB_NAME', 'predictive_maintenance')
        self.client = MongoClient(uri)
        self.db = self.client[db]
        
        self.notifier = EmailNotifier(mongo_uri=uri, db_name=db)
        self.hc = AssetHealthCalculator()
        self.fe = FinancialEngine()
        
        self.models = {}
        self.load_models()
        
        self.thresholds = {}
        for target in getattr(config, 'WIND_NBM_TARGETS', []):
            self.thresholds[target] = {'warning': 5.0, 'critical': 10.0}
            
    def load_models(self):
        save_dir = getattr(config, 'MODEL_SAVE_DIR', 'models/')
        targets = getattr(config, 'WIND_NBM_TARGETS', [])
        for target in targets:
            model_path = os.path.join(save_dir, f"nbm_{target}.joblib")
            if os.path.exists(model_path):
                self.models[target] = joblib.load(model_path)
                print(f"Loaded model for {target}")
            else:
                print(f"Warning: Model not found at {model_path}")
                
        solar_model_path = os.path.join(save_dir, "nbm_solar_ac_power.joblib")
        if os.path.exists(solar_model_path):
            self.models['solar_ac_power'] = joblib.load(solar_model_path)
            print("Loaded Solar NBM model (solar_ac_power)")

    def score_wind_telemetry(self, doc: dict) -> dict:
        scores = {}
        overall_score = 0.0
        
        features = getattr(config, 'WIND_NBM_FEATURES', [])
        feature_vals = []
        missing_features = False
        for f in features:
            if f in doc:
                feature_vals.append(doc[f])
            else:
                missing_features = True
                break
                
        if not missing_features and len(self.models) > 0:
            import pandas as pd
            X = pd.DataFrame([dict(zip(features, feature_vals))])
            for target, model in self.models.items():
                if target in doc and target in self.thresholds:
                    pred = model.predict(X)[0]
                    actual = doc[target]
                    residual = abs(actual - pred)
                    
                    crit_thresh = self.thresholds[target]['critical']
                    score = min(100.0, (residual / crit_thresh) * 100.0)
                    scores[target] = score
                    if score > overall_score:
                        overall_score = score
                        
        # --- Differential Temperature Delta (Delta T = Bearing - Oil) ---
        gb_bearing = doc.get('gearbox_bearing_temp')
        gb_oil = doc.get('gearbox_oil_temp')
        if gb_bearing is not None and gb_oil is not None:
            delta_t = gb_bearing - gb_oil
            # Normal delta T is 10-15°C. Spikes above 20°C indicate severe localized friction.
            if delta_t > 20.0:
                delta_score = min(100.0, (delta_t - 20.0) * 5.0)
                scores['thermal_delta_gearbox'] = delta_score
                overall_score = max(overall_score, delta_score)

        # --- 3-Phase Electrical Current Imbalance (Delta I) ---
        i1 = doc.get('current_phase_1')
        i2 = doc.get('current_phase_2')
        i3 = doc.get('current_phase_3')
        if i1 is not None and i2 is not None and i3 is not None:
            i_avg = (i1 + i2 + i3) / 3.0
            if i_avg > 10.0:
                max_dev = max(abs(i1 - i_avg), abs(i2 - i_avg), abs(i3 - i_avg))
                imbalance_pct = (max_dev / i_avg) * 100.0
                doc['electrical_imbalance_pct'] = round(imbalance_pct, 2)
                if imbalance_pct > 5.0:
                    elec_score = min(100.0, (imbalance_pct - 5.0) * 10.0)
                    scores['electrical_imbalance'] = elec_score
                    overall_score = max(overall_score, elec_score)

        gen_rpm_std = doc.get('generator_rpm_std')
        rotor_rpm_std = doc.get('rotor_rpm_std')
        vib_score = 0.0
        if gen_rpm_std is not None and gen_rpm_std > 30.0:  # arbitrary threshold for 2x normal
            vib_score = min(100.0, (gen_rpm_std / 30.0) * 50.0)
        if rotor_rpm_std is not None and rotor_rpm_std > 2.4:
            vib_score = max(vib_score, min(100.0, (rotor_rpm_std / 2.4) * 50.0))
            
        scores['vibration'] = vib_score
        overall_score = max(overall_score, vib_score)
        
        scores['overall'] = overall_score
        return scores

    def score_solar_telemetry(self, doc: dict) -> dict:
        scores = {}
        overall_score = 0.0
        
        irradiance = doc.get('solar_irradiance')
        ambient_temp = doc.get('ambient_temp')
        panel_temp = doc.get('panel_temp')
        actual_power = doc.get('power_output_kw')
        capacity = doc.get('capacity_kw', 10)
        
        # --- IEC 61724 Solar Performance Ratio (PR) ---
        if irradiance is not None and irradiance > 200 and actual_power is not None:
            expected_ref_power = (irradiance / 1000.0) * capacity
            if expected_ref_power > 0:
                pr = actual_power / expected_ref_power
                doc['performance_ratio'] = round(pr, 3)
                if pr < 0.70:
                    pr_score = min(100.0, (0.80 - pr) * 250.0)
                    scores['performance_ratio_drop'] = pr_score
                    overall_score = max(overall_score, pr_score)

        # ML NBM Prediction for Solar Expected Power
        expected_power = doc.get('expected_power_kw')
        if 'solar_ac_power' in self.models and irradiance is not None and ambient_temp is not None and panel_temp is not None:
            import pandas as pd
            X = pd.DataFrame([{
                'IRRADIATION': irradiance,
                'AMBIENT_TEMPERATURE': ambient_temp,
                'MODULE_TEMPERATURE': panel_temp
            }])
            # Model predicts in kW (or scaled)
            predicted_power_raw = float(self.models['solar_ac_power'].predict(X)[0])
            # Apply Inverter Clipping Guard (capacity ceiling cap)
            expected_power = min(predicted_power_raw, capacity)

        if expected_power is not None and actual_power is not None and irradiance is not None and irradiance > 100:
            # Require actual power to drop below 85% of expected before scoring power deficit to ignore minor thermal variance & clipping
            if actual_power < (expected_power * 0.85):
                power_residual = max(0.0, expected_power - actual_power)
                power_anomaly = min(100.0, (power_residual / expected_power) * 100.0)
                scores['power_deficit'] = power_anomaly
                overall_score = max(overall_score, power_anomaly)
            else:
                scores['power_deficit'] = 0.0
        
        soiling = doc.get('soiling_factor')
        if soiling is not None and soiling < 0.85:
            scores['soiling'] = min(100.0, (0.85 - soiling) * 500)
            overall_score = max(overall_score, scores['soiling'])
            
        has_fault = doc.get('has_diode_fault')
        if has_fault:
            scores['diode'] = 100.0
            overall_score = max(overall_score, 100.0)
            
        scores['overall'] = overall_score
        return scores

    def run_scoring_loop(self, interval_seconds=10):
        print("Starting anomaly scoring loop...")
        telemetry_coll = self.db[getattr(config, 'COLLECTION_TELEMETRY', 'telemetry_live')]
        anomaly_coll = self.db[getattr(config, 'COLLECTION_ANOMALY_SCORES', 'anomaly_scores')]
        
        while True:
            cursor = telemetry_coll.find({'anomaly_scores': {'$exists': False}})
            count = 0
            for doc in cursor:
                asset_type = doc.get('asset_type')
                
                if asset_type == 'wind_turbine':
                    scores = self.score_wind_telemetry(doc)
                elif asset_type == 'solar_panel':
                    scores = self.score_solar_telemetry(doc)
                else:
                    scores = {'overall': 0.0}
                    
                telemetry_coll.update_one({'_id': doc['_id']}, {'$set': {'anomaly_scores': scores}})
                
                anomaly_doc = {
                    'asset_id': doc.get('asset_id'),
                    'timestamp': doc.get('timestamp'),
                    'scores': scores
                }
                anomaly_coll.insert_one(anomaly_doc)
                count += 1

                # Check if asset AHI collapsed below Warning (< 50 AHI) threshold
                ahi = max(0.0, 100.0 - scores.get('overall', 0.0))
                if ahi < 50.0:
                    aid = doc.get('asset_id', 'Unknown')
                    atype = doc.get('asset_type', 'unknown')
                    region = doc.get('region', 'Temperate')
                    reg_info = getattr(config, 'REGIONAL_MODIFIERS', {}).get(region, {})
                    oem = reg_info.get('oem_wind' if atype == 'wind_turbine' else 'oem_solar', 'Generic OEM Hardware')

                    top_issue = 'General Degradation'
                    max_score = 0.0
                    for k, v in scores.items():
                        if k != 'overall' and isinstance(v, (int, float)) and v > max_score:
                            max_score = v
                            top_issue = k

                    lead_days = getattr(config, 'PROCUREMENT_LEAD_TIMES', {}).get(top_issue, 14)
                    cap = getattr(config, 'WIND_TURBINE_CAPACITY_KW', 2000) if atype == 'wind_turbine' else getattr(config, 'SOLAR_PANEL_CAPACITY_KW', 10)
                    actual = doc.get('active_power') or doc.get('power_output_kw') or 0
                    expected = doc.get('expected_power_kw')
                    
                    loss_kw = self.fe.estimate_hourly_power_loss(cap, actual, expected, status_type_id=doc.get('status_type_id', 0), ahi=ahi)
                    daily_loss = self.fe.estimate_revenue_loss(loss_kw)
                    repair_cost = self.fe.estimate_repair_cost(ahi)
                    
                    rec = self.fe.generate_recommendation(aid, atype, ahi, scores, daily_loss)
                    health_status = rec.get('health_status', self.hc.classify_health(ahi))
                    action = rec.get('recommended_action', f'Inspect primary component: {top_issue}')
                    
                    self.notifier.send_alert_email(
                        asset_id=aid,
                        asset_type=atype,
                        region=region,
                        oem=oem,
                        ahi=ahi,
                        health_status=health_status,
                        top_issue=top_issue,
                        lead_days=lead_days,
                        daily_loss=daily_loss,
                        repair_cost=repair_cost,
                        action=action
                    )
                
            if count > 0:
                print(f"Scored {count} documents.")
                
            time.sleep(interval_seconds)

if __name__ == '__main__':
    scorer = AnomalyScorer()
    scorer.run_scoring_loop()
