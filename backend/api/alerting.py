import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class AlertManager:
    """Real-time alerting and notification system"""
    
    def __init__(self):
        self.alert_rules = []
        self.active_alerts = []
        self.notification_channels = {
            'email': {'enabled': True, 'config': {}},
            'slack': {'enabled': False, 'config': {}},
            'webhook': {'enabled': False, 'config': {}}
        }
        self.alert_history = []
        
    def create_alert_rule(self, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert rule"""
        rule = {
            'id': f"alert_{len(self.alert_rules) + 1}",
            'name': rule_config.get('name'),
            'metric': rule_config.get('metric'),
            'condition': rule_config.get('condition'),
            'threshold': rule_config.get('threshold'),
            'severity': rule_config.get('severity', 'medium'),
            'enabled': rule_config.get('enabled', True),
            'notification_channels': rule_config.get('notification_channels', ['email']),
            'created_at': datetime.now().isoformat(),
            'cooldown_minutes': rule_config.get('cooldown_minutes', 5)
        }
        
        self.alert_rules.append(rule)
        logger.info(f"Created alert rule: {rule['name']}")
        return rule
    
    def evaluate_metrics(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate metrics against alert rules"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if not rule['enabled']:
                continue
                
            metric_value = metrics_data.get(rule['metric'], 0)
            threshold = rule['threshold']
            condition = rule['condition']
            
            # Check if alert should trigger
            triggered = self._evaluate_condition(metric_value, condition, threshold)
            
            if triggered:
                # Check cooldown period
                if not self._is_in_cooldown(rule):
                    alert = self._create_alert(rule, metric_value)
                    triggered_alerts.append(alert)
                    self.active_alerts.append(alert)
                    
                    # Send notifications
                    asyncio.create_task(self._send_notifications(alert))
        
        return triggered_alerts
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == 'greater_than':
            return value > threshold
        elif condition == 'less_than':
            return value < threshold
        elif condition == 'equals':
            return value == threshold
        elif condition == 'not_equals':
            return value != threshold
        elif condition == 'percentage_increase':
            return (value / threshold - 1) * 100 > 20  # 20% increase
        return False
    
    def _is_in_cooldown(self, rule: Dict[str, Any]) -> bool:
        """Check if alert is in cooldown period"""
        rule_id = rule['id']
        cooldown_minutes = rule['cooldown_minutes']
        
        # Check recent alerts for this rule
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.get('rule_id') == rule_id and
            datetime.fromisoformat(alert['created_at']) > datetime.now() - timedelta(minutes=cooldown_minutes)
        ]
        
        return len(recent_alerts) > 0
    
    def _create_alert(self, rule: Dict[str, Any], metric_value: float) -> Dict[str, Any]:
        """Create alert object"""
        alert = {
            'id': f"alert_{len(self.alert_history) + 1}",
            'rule_id': rule['id'],
            'rule_name': rule['name'],
            'severity': rule['severity'],
            'metric': rule['metric'],
            'current_value': metric_value,
            'threshold': rule['threshold'],
            'condition': rule['condition'],
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'message': self._generate_alert_message(rule, metric_value),
            'notification_sent': False
        }
        
        self.alert_history.append(alert)
        return alert
    
    def _generate_alert_message(self, rule: Dict[str, Any], metric_value: float) -> str:
        """Generate human-readable alert message"""
        condition_map = {
            'greater_than': 'exceeded',
            'less_than': 'fell below',
            'equals': 'equals',
            'not_equals': 'does not equal'
        }
        
        condition_text = condition_map.get(rule['condition'], 'triggered')
        metric_name = rule['metric'].replace('_', ' ').title()
        
        return f"🚨 ALERT: {metric_name} has {condition_text} threshold of {rule['threshold'] (current: {metric_value})"
    
    async def _send_notifications(self, alert: Dict[str, Any]) -> None:
        """Send notifications through configured channels"""
        channels = alert.get('notification_channels', ['email'])
        
        for channel in channels:
            if self.notification_channels.get(channel, {}).get('enabled', False):
                try:
                    if channel == 'email':
                        await self._send_email_notification(alert)
                    elif channel == 'slack':
                        await self._send_slack_notification(alert)
                    elif channel == 'webhook':
                        await self._send_webhook_notification(alert)
                    
                    # Mark notification as sent
                    alert['notification_sent'] = True
                    logger.info(f"Notification sent via {channel} for alert {alert['id']}")
                    
                except Exception as e:
                    logger.error(f"Failed to send {channel} notification: {str(e)}")
    
    async def _send_email_notification(self, alert: Dict[str, Any]) -> None:
        """Send email notification"""
        try:
            # Simulate email sending (in production, use actual SMTP)
            msg = MIMEMultipart()
            msg['From'] = 'sre-alerts@company.com'
            msg['To'] = 'sre-team@company.com'
            msg['Subject'] = f"SRE Alert: {alert['rule_name']}"
            
            body = f"""
            Alert Details:
            - Rule: {alert['rule_name']}
            - Metric: {alert['metric']}
            - Current Value: {alert['current_value']}
            - Threshold: {alert['threshold']}
            - Severity: {alert['severity']}
            - Time: {alert['created_at']}
            
            Message: {alert['message']}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # In production, actually send the email
            # server = smtplib.SMTP('smtp.company.com', 587)
            # server.starttls()
            # server.login('user', 'password')
            # server.send_message(msg)
            # server.quit()
            
            logger.info(f"Email notification sent for alert {alert['id']}")
            
        except Exception as e:
            logger.error(f"Email notification failed: {str(e)}")
    
    async def _send_slack_notification(self, alert: Dict[str, Any]) -> None:
        """Send Slack notification"""
        # Simulate Slack webhook call
        slack_payload = {
            "text": alert['message'],
            "attachments": [{
                "color": self._get_severity_color(alert['severity']),
                "fields": [
                    {"title": "Metric", "value": alert['metric'], "short": True},
                    {"title": "Current", "value": str(alert['current_value']), "short": True},
                    {"title": "Threshold", "value": str(alert['threshold']), "short": True},
                    {"title": "Severity", "value": alert['severity'], "short": True}
                ]
            }]
        }
        
        # In production, make actual webhook call
        # requests.post(webhook_url, json=slack_payload)
        logger.info(f"Slack notification sent for alert {alert['id']}")
    
    async def _send_webhook_notification(self, alert: Dict[str, Any]) -> None:
        """Send webhook notification"""
        webhook_payload = {
            "alert_id": alert['id'],
            "rule_name": alert['rule_name'],
            "severity": alert['severity'],
            "metric": alert['metric'],
            "current_value": alert['current_value'],
            "threshold": alert['threshold'],
            "message": alert['message'],
            "timestamp": alert['created_at']
        }
        
        # In production, make actual webhook call
        # requests.post(webhook_url, json=webhook_payload)
        logger.info(f"Webhook notification sent for alert {alert['id']}")
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for Slack notification based on severity"""
        colors = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'warning',
            'low': 'good'
        }
        return colors.get(severity, 'warning')
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return [alert for alert in self.active_alerts if alert['status'] == 'active']
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.active_alerts:
            if alert['id'] == alert_id:
                alert['status'] = 'acknowledged'
                alert['acknowledged_at'] = datetime.now().isoformat()
                logger.info(f"Alert {alert_id} acknowledged")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.active_alerts:
            if alert['id'] == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now().isoformat()
                # Remove from active alerts
                self.active_alerts.remove(alert)
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False

# Global alert manager instance
alert_manager = AlertManager()

# Initialize default alert rules
default_rules = [
    {
        'name': 'High Error Rate',
        'metric': 'error_rate',
        'condition': 'greater_than',
        'threshold': 5.0,
        'severity': 'high',
        'notification_channels': ['email']
    },
    {
        'name': 'High Response Time',
        'metric': 'response_time_avg',
        'condition': 'greater_than',
        'threshold': 1000.0,
        'severity': 'medium',
        'notification_channels': ['email']
    },
    {
        'name': 'Low Availability',
        'metric': 'availability_percentage',
        'condition': 'less_than',
        'threshold': 99.0,
        'severity': 'critical',
        'notification_channels': ['email', 'slack']
    }
]

for rule in default_rules:
    alert_manager.create_alert_rule(rule)
