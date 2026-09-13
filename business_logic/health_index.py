class AssetHealthCalculator:
    def calculate_ahi(self, anomaly_scores: dict) -> float:
        overall = anomaly_scores.get('overall', 0.0)
        ahi = 100.0 - overall
        return max(0.0, min(100.0, ahi))

    def calculate_degradation_rate(self, score_history: list) -> float:
        if len(score_history) < 2:
            return 0.0
            
        import numpy as np
        
        # Sort by timestamp
        sorted_hist = sorted(score_history, key=lambda x: x.get('timestamp'))
        
        times = [d.get('timestamp').timestamp() for d in sorted_hist]
        scores = [d.get('scores', {}).get('overall', 0.0) for d in sorted_hist]
        
        # Convert times to hours from first timestamp
        t0 = times[0]
        hours = [(t - t0) / 3600.0 for t in times]
        
        if len(set(hours)) < 2:
            return 0.0
            
        slope, _ = np.polyfit(hours, scores, 1)
        return float(slope)

    def estimate_rul_hours(self, current_ahi: float, score_history: list) -> dict:
        """Estimate Remaining Useful Life (RUL) in operating hours based on degradation velocity."""
        rate = self.calculate_degradation_rate(score_history)
        
        # Default RUL for healthy assets
        if current_ahi >= 90.0 or rate <= 0.01:
            return {'rul_hours': 720.0, 'velocity': 'Stable', 'is_collapsing': False}  # ~30 days
            
        # Velocity in AHI points lost per hour
        # If rate is positive (anomaly score increasing), health is dropping
        ahi_drop_per_hour = abs(rate)
        if ahi_drop_per_hour > 0:
            rul = current_ahi / ahi_drop_per_hour
        else:
            rul = 720.0
            
        rul = max(0.5, min(720.0, float(rul)))
        velocity = 'Fast' if ahi_drop_per_hour > 5.0 else 'Moderate' if ahi_drop_per_hour > 1.0 else 'Slow'
        is_collapsing = ahi_drop_per_hour > 5.0 or rul < 24.0
        
        return {
            'rul_hours': round(rul, 1),
            'velocity': velocity,
            'is_collapsing': is_collapsing
        }

    def classify_health(self, ahi: float) -> str:
        if ahi >= 80:
            return 'Healthy'
        elif ahi >= 50:
            return 'At Risk'
        elif ahi >= 20:
            return 'Degraded'
        else:
            return 'Critical'

    def get_color(self, ahi: float) -> str:
        if ahi >= 80:
            return '#00FF00'  # Green
        elif ahi >= 50:
            return '#FFFF00'  # Yellow
        elif ahi >= 20:
            return '#FFA500'  # Orange
        else:
            return '#FF0000'  # Red
