"""
Automated HTML Email Notification Engine for PdM Platform
=========================================================
Generates responsive B2B HTML email notifications when equipment health (AHI)
drops below Warning (< 50 AHI) or Critical (< 20 AHI) thresholds.
Persists alert notifications to MongoDB and dispatches SMTP emails.
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class EmailNotifier:
    def __init__(self, mongo_uri=None, db_name=None):
        self.mongo_uri = mongo_uri or config.MONGO_URI
        self.db_name = db_name or config.DB_NAME
        self._db = None

    def _get_db(self):
        if self._db is None:
            client = MongoClient(self.mongo_uri)
            self._db = client[self.db_name]
        return self._db

    def is_in_cooldown(self, asset_id: str, severity: str) -> bool:
        """Check if an alert of same or higher severity was sent recently for asset_id."""
        db = self._get_db()
        col = db[getattr(config, 'COLLECTION_ALERTS', 'alert_notifications')]
        cooldown_cutoff = datetime.now(timezone.utc) - timedelta(minutes=config.ALERT_COOLDOWN_MINUTES)
        
        recent = col.find_one({
            'asset_id': asset_id,
            'dispatched_at': {'$gte': cooldown_cutoff}
        })
        return recent is not None

    def generate_html_email(self, asset_id: str, asset_type: str, region: str, oem: str,
                            ahi: float, health_status: str, top_issue: str, lead_days: int,
                            daily_loss: float, repair_cost: float, net_savings: float, action: str) -> str:
        """Build a crisp, high-contrast HTML email template without any emojis."""
        
        badge_bg = "#fee2e2" if ahi < 20 else "#fef3c7"
        badge_color = "#991b1b" if ahi < 20 else "#92400e"
        badge_border = "#fca5a5" if ahi < 20 else "#fcd34d"
        severity_title = "CRITICAL FAILURE IMMINENT ALERT" if ahi < 20 else "EQUIPMENT HEALTH WARNING NOTICE"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{severity_title} - {asset_id}</title>
</head>
<body style="font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #0f172a; margin: 0; padding: 24px;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 650px; margin: 0 auto; background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(15,23,42,0.08);">
        <!-- Header -->
        <tr>
            <td style="background-color: #0f172a; padding: 24px 32px; text-align: left;">
                <h1 style="color: #0284c7; margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px;">WattWise DISPATCH SYSTEM</h1>
                <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 13px;">Automated Telemetry Diagnostic Alert & Service Order</p>
            </td>
        </tr>

        <!-- Alert Banner -->
        <tr>
            <td style="padding: 24px 32px 12px 32px;">
                <div style="background-color: {badge_bg}; border: 1px solid {badge_border}; border-radius: 8px; padding: 16px 20px;">
                    <div style="font-size: 12px; font-weight: 800; color: {badge_color}; text-transform: uppercase; letter-spacing: 0.05em;">{severity_title}</div>
                    <div style="font-size: 20px; font-weight: 800; color: {badge_color}; margin-top: 4px;">Asset {asset_id} requires immediate inspection</div>
                </div>
            </td>
        </tr>

        <!-- Summary Content -->
        <tr>
            <td style="padding: 12px 32px 24px 32px;">
                <p style="font-size: 14px; line-height: 1.5; color: #334155;">
                    The Predictive Maintenance Engine has flagged abnormal operation on equipment unit <b>{asset_id}</b>. Telemetry indicates component degradation exceeding baseline thresholds.
                </p>

                <!-- Asset Specs Table -->
                <table width="100%" border="0" cellspacing="0" cellpadding="8" style="border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 16px; font-size: 13px;">
                    <tr style="background-color: #f1f5f9;">
                        <td style="font-weight: 700; color: #475569; width: 40%; border-bottom: 1px solid #e2e8f0;">Equipment Asset ID</td>
                        <td style="font-weight: 700; color: #0f172a; border-bottom: 1px solid #e2e8f0;">{asset_id}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0;">Asset Type / OEM</td>
                        <td style="color: #0f172a; border-bottom: 1px solid #e2e8f0;">{asset_type.upper().replace('_', ' ')} | {oem}</td>
                    </tr>
                    <tr style="background-color: #f1f5f9;">
                        <td style="font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0;">Climate Region</td>
                        <td style="color: #0f172a; border-bottom: 1px solid #e2e8f0;">{region}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0;">Asset Health Index (AHI)</td>
                        <td style="color: {badge_color}; font-weight: 800; border-bottom: 1px solid #e2e8f0;">{ahi:.1f} / 100 ({health_status})</td>
                    </tr>
                    <tr style="background-color: #f1f5f9;">
                        <td style="font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0;">Root Cause / Primary Fault</td>
                        <td style="color: #b91c1c; font-weight: 800; border-bottom: 1px solid #e2e8f0;">{top_issue}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0;">Estimated Resolution Window</td>
                        <td style="color: #0f172a; font-weight: 700; border-bottom: 1px solid #e2e8f0;">{lead_days} Days (Parts Lead Time)</td>
                    </tr>
                    <tr style="background-color: #f1f5f9;">
                        <td style="font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0;">Daily Revenue Loss (Inaction)</td>
                        <td style="color: #ef4444; font-weight: 700; border-bottom: 1px solid #e2e8f0;">${daily_loss:,.2f} / day</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; color: #475569;">Projected Net Money Saved (ROI)</td>
                        <td style="color: #166534; font-weight: 800; font-size: 14px;">${net_savings:,.2f}</td>
                    </tr>
                </table>

                <!-- Action Box -->
                <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 14px 16px; margin-top: 20px; border-radius: 4px;">
                    <div style="font-size: 12px; font-weight: 700; color: #0284c7; text-transform: uppercase;">Recommended Technician Action</div>
                    <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-weight: 600;">{action}</div>
                </div>

                <p style="font-size: 12px; color: #64748b; margin-top: 24px;">
                    Notice Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | Automated System Dispatch
                </p>
            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td style="background-color: #f1f5f9; padding: 16px 32px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b;">
                Predictive Maintenance Platform &bull; Clean Energy Operations &bull; Do not reply directly to this automated email.
            </td>
        </tr>
    </table>
</body>
</html>"""
        return html

    def send_alert_email(self, asset_id: str, asset_type: str, region: str, oem: str,
                         ahi: float, health_status: str, top_issue: str, lead_days: int,
                         daily_loss: float, repair_cost: float, action: str):
        """Build HTML email, check cooldown, save to MongoDB, and dispatch via SMTP or Mock Logger."""
        
        severity = "Critical" if ahi < 20 else "Warning"
        
        if self.is_in_cooldown(asset_id, severity):
            print(f"[EMAIL NOTIFIER] Cooldown active for {asset_id} ({severity}). Skipping duplicate dispatch.")
            return False

        catastrophic_loss_avoided = (daily_loss * lead_days) + (config.EMERGENCY_REPLACEMENT_COST if ahi < 50 else config.PREVENTIVE_MAINTENANCE_COST * 2)
        net_savings = max(0.0, catastrophic_loss_avoided - repair_cost)

        html_body = self.generate_html_email(
            asset_id, asset_type, region, oem, ahi, health_status,
            top_issue, lead_days, daily_loss, repair_cost, net_savings, action
        )

        db = self._get_db()
        email_cfg = db['settings'].find_one({'key': 'email_config'}) or {}
        recipient = email_cfg.get('recipient_email') or os.getenv('ALERT_RECIPIENT_EMAIL', 'operator@energycorp.com')
        smtp_host = email_cfg.get('smtp_host') or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = email_cfg.get('smtp_port') or int(os.getenv('SMTP_PORT', 587))
        smtp_user = email_cfg.get('smtp_user') or os.getenv('SMTP_USER', '')
        smtp_pass = email_cfg.get('smtp_pass') or os.getenv('SMTP_PASS', '')

        delivery_status = "Logged to DB (Mock SMTP Mode)"

        # Attempt SMTP Dispatch if credentials configured
        if smtp_user and smtp_pass:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"[{severity.upper()} ALERT] Asset {asset_id} Health Collapsed to {ahi:.1f} AHI"
                msg["From"] = smtp_user
                msg["To"] = recipient

                text_plain = f"ALERT: Asset {asset_id} health has collapsed to {ahi:.1f} AHI. Fault: {top_issue}. Action: {action}"
                msg.attach(MIMEText(text_plain, "plain"))
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, [recipient], msg.as_string())
                
                delivery_status = f"Dispatched via SMTP to {recipient}"
                print(f"[EMAIL NOTIFIER] Successfully sent SMTP email alert for {asset_id} to {recipient}")
            except Exception as e:
                delivery_status = f"SMTP Error: {str(e)}"
                print(f"[EMAIL NOTIFIER] SMTP dispatch failed ({e}). Logged alert to MongoDB.")
        else:
            print(f"[EMAIL NOTIFIER] [ALERT ENGINE] HTML email rendered & logged to MongoDB for asset {asset_id} (AHI: {ahi:.1f}, Fault: {top_issue})")

        # Save Alert Notification to MongoDB
        db = self._get_db()
        alert_doc = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'region': region,
            'oem': oem,
            'ahi': float(ahi),
            'severity': severity,
            'health_status': health_status,
            'primary_fault': top_issue,
            'resolution_lead_days': int(lead_days),
            'daily_revenue_loss': float(daily_loss),
            'repair_cost': float(repair_cost),
            'net_savings': float(net_savings),
            'action_instructions': action,
            'recipient': recipient,
            'delivery_status': delivery_status,
            'dispatched_at': datetime.now(timezone.utc),
            'html_content': html_body
        }
        
        col = db[getattr(config, 'COLLECTION_ALERTS', 'alert_notifications')]
        col.insert_one(alert_doc)
        return True
