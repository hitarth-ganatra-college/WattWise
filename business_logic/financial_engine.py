import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from business_logic.health_index import AssetHealthCalculator

class FinancialEngine:
    def estimate_hourly_power_loss(self, capacity_kw: float, current_power_kw: float, expected_power_kw: float = None, status_type_id: int = 0, ahi: float = 100.0) -> float:
        # Grid Curtailment Guard: Status 1 (Derated) & Status 2 (Idling) without component faults (AHI >= 80) mean grid operator commanded throttling.
        if status_type_id in [1, 2] and ahi >= 80.0:
            return 0.0

        if expected_power_kw is not None:
            loss = expected_power_kw - current_power_kw
        else:
            loss = capacity_kw * 0.3 - current_power_kw
        return max(0.0, loss)

    def estimate_revenue_loss(self, power_loss_kw: float, hours: float = 24, price_per_kwh: float = None) -> float:
        price = price_per_kwh if price_per_kwh is not None else getattr(config, 'ELECTRICITY_PRICE_PER_KWH', 0.10)
        return power_loss_kw * hours * price

    def estimate_repair_cost(self, ahi: float) -> float:
        emer_cost = getattr(config, 'EMERGENCY_REPLACEMENT_COST', 50000)
        prev_cost = getattr(config, 'PREVENTIVE_MAINTENANCE_COST', 5000)
        
        if ahi < 20:
            return emer_cost
        if ahi < 50:
            return prev_cost
        return prev_cost * 0.5

    def calculate_priority_score(self, ahi: float, revenue_loss_daily: float, lead_time_days: int = 7) -> float:
        # RPN factors failure probability (100 - AHI), daily revenue loss, and procurement lead time risk
        lead_time_factor = 1.0 + (lead_time_days / 30.0)
        rpn = (100.0 - ahi) * revenue_loss_daily * lead_time_factor / 100.0
        return round(rpn, 2)

    def generate_recommendation(self, asset_id: str, asset_type: str, ahi: float, anomaly_details: dict, revenue_loss: float) -> dict:
        hc = AssetHealthCalculator()
        health_status = hc.classify_health(ahi)
        
        top_issue = None
        max_score = -1
        for k, v in anomaly_details.items():
            if k != 'overall' and v > max_score:
                max_score = v
                top_issue = k
                
        lead_times = getattr(config, 'PROCUREMENT_LEAD_TIMES', {})
        lead_time_days = lead_times.get(top_issue, 7) if top_issue else 1

        urgency = 'Monitor'
        action = 'Continue normal operations.'
        if ahi < 20:
            urgency = 'Immediate'
            action = f'Immediate emergency repair required for {top_issue}. (Procurement Lead Time: {lead_time_days} Days)'
        elif ahi < 50:
            urgency = 'This Week'
            action = f'Schedule maintenance for {top_issue} this week. (Order parts now - Lead Time: {lead_time_days} Days)'
        elif ahi < 80:
            urgency = 'Scheduled'
            action = f'Inspect {top_issue} during next scheduled maintenance. (Lead Time: {lead_time_days} Days)'
            
        rpn = self.calculate_priority_score(ahi, revenue_loss, lead_time_days)
            
        return {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'health_status': health_status,
            'ahi': ahi,
            'priority_score': rpn,
            'estimated_daily_revenue_loss': revenue_loss,
            'estimated_repair_cost': self.estimate_repair_cost(ahi),
            'top_issue': top_issue or 'None',
            'lead_time_days': lead_time_days,
            'recommended_action': action,
            'urgency': urgency
        }
