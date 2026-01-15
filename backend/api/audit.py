import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class AuditLogger:
    """Comprehensive logging and audit trail system"""
    
    def __init__(self):
        self.audit_logs = []
        self.session_logs = []
        self.access_logs = []
        self.system_events = []
        
    def log_user_action(self, user_id: str, action: str, resource: str, 
                       details: Dict[str, Any] = None, ip_address: str = None) -> None:
        """Log user actions for audit trail"""
        audit_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'resource_type': self._get_resource_type(resource),
            'details': details or {},
            'ip_address': ip_address,
            'user_agent': details.get('user_agent') if details else None,
            'session_id': details.get('session_id') if details else None,
            'outcome': 'success',
            'category': 'user_action'
        }
        
        self.audit_logs.append(audit_entry)
        logger.info(f"User action logged: {user_id} - {action} on {resource}")
        
        # Keep only last 1000 audit entries
        if len(self.audit_logs) > 1000:
            self.audit_logs.pop(0)
    
    def log_system_event(self, event_type: str, severity: str, message: str,
                       source: str = None, metadata: Dict[str, Any] = None) -> None:
        """Log system events"""
        system_event = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'message': message,
            'source': source or 'system',
            'metadata': metadata or {},
            'category': 'system_event'
        }
        
        self.system_events.append(system_event)
        logger.info(f"System event logged: {event_type} - {severity} - {message}")
        
        # Keep only last 500 system events
        if len(self.system_events) > 500:
            self.system_events.pop(0)
    
    def log_access_attempt(self, user_id: str, resource: str, success: bool,
                        ip_address: str = None, failure_reason: str = None) -> None:
        """Log access attempts"""
        access_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'access_type': self._get_resource_type(resource),
            'success': success,
            'ip_address': ip_address,
            'failure_reason': failure_reason,
            'category': 'access_attempt'
        }
        
        self.access_logs.append(access_entry)
        logger.info(f"Access attempt logged: {user_id} - {resource} - {success}")
        
        # Keep only last 1000 access logs
        if len(self.access_logs) > 1000:
            self.access_logs.pop(0)
    
    def log_incident_lifecycle(self, incident_id: str, action: str, user_id: str = None,
                             details: Dict[str, Any] = None) -> None:
        """Log incident lifecycle events"""
        incident_event = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'incident_id': incident_id,
            'action': action,  # created, updated, assigned, resolved, closed
            'user_id': user_id,
            'details': details or {},
            'category': 'incident_lifecycle'
        }
        
        self.audit_logs.append(incident_event)
        logger.info(f"Incident lifecycle logged: {incident_id} - {action}")
    
    def log_configuration_change(self, config_item: str, old_value: Any, new_value: Any,
                              user_id: str, reason: str = None) -> None:
        """Log configuration changes"""
        config_change = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'config_item': config_item,
            'old_value': old_value,
            'new_value': new_value,
            'user_id': user_id,
            'reason': reason,
            'category': 'configuration_change'
        }
        
        self.audit_logs.append(config_change)
        logger.info(f"Configuration change logged: {config_item} by {user_id}")
    
    def log_api_access(self, endpoint: str, method: str, user_id: str = None,
                     status_code: int = None, response_time: float = None,
                     request_size: int = None, ip_address: str = None) -> None:
        """Log API access"""
        api_access = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'user_id': user_id,
            'status_code': status_code,
            'response_time': response_time,
            'request_size': request_size,
            'ip_address': ip_address,
            'category': 'api_access'
        }
        
        self.audit_logs.append(api_access)
        logger.info(f"API access logged: {method} {endpoint} - {status_code}")
    
    def get_audit_logs(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        logs = self.audit_logs.copy()
        
        if filters:
            # Filter by user_id
            if 'user_id' in filters:
                logs = [log for log in logs if log.get('user_id') == filters['user_id']]
            
            # Filter by category
            if 'category' in filters:
                logs = [log for log in logs if log.get('category') == filters['category']]
            
            # Filter by date range
            if 'start_date' in filters:
                start_date = datetime.fromisoformat(filters['start_date'])
                logs = [log for log in logs if datetime.fromisoformat(log['timestamp']) >= start_date]
            
            if 'end_date' in filters:
                end_date = datetime.fromisoformat(filters['end_date'])
                logs = [log for log in logs if datetime.fromisoformat(log['timestamp']) <= end_date]
            
            # Filter by resource
            if 'resource' in filters:
                logs = [log for log in logs if filters['resource'] in log.get('resource', '')]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs
    
    def get_access_logs(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get access logs with optional filtering"""
        logs = self.access_logs.copy()
        
        if filters:
            # Filter by success
            if 'success' in filters:
                logs = [log for log in logs if log.get('success') == filters['success']]
            
            # Filter by date range
            if 'start_date' in filters:
                start_date = datetime.fromisoformat(filters['start_date'])
                logs = [log for log in logs if datetime.fromisoformat(log['timestamp']) >= start_date]
        
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs
    
    def get_system_events(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get system events with optional filtering"""
        events = self.system_events.copy()
        
        if filters:
            # Filter by severity
            if 'severity' in filters:
                events = [event for event in events if event.get('severity') == filters['severity']]
            
            # Filter by event type
            if 'event_type' in filters:
                events = [event for event in events if event.get('event_type') == filters['event_type']]
        
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        return events
    
    def generate_compliance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate compliance report"""
        logs = self.get_audit_logs({
            'start_date': start_date,
            'end_date': end_date
        })
        
        # Analyze compliance metrics
        total_actions = len(logs)
        failed_access = len([log for log in self.access_logs 
                          if not log.get('success', True) and 
                          start_date <= log['timestamp'] <= end_date])
        
        critical_events = len([event for event in self.system_events 
                            if event.get('severity') == 'critical' and
                            start_date <= event['timestamp'] <= end_date])
        
        return {
            'report_period': f"{start_date} to {end_date}",
            'total_user_actions': total_actions,
            'failed_access_attempts': failed_access,
            'critical_system_events': critical_events,
            'compliance_score': max(0, 100 - (failed_access * 2) - (critical_events * 5)),
            'recommendations': self._generate_compliance_recommendations(failed_access, critical_events)
        }
    
    def _get_resource_type(self, resource: str) -> str:
        """Determine resource type from resource identifier"""
        if '/incidents' in resource:
            return 'incident'
        elif '/alerts' in resource:
            return 'alert'
        elif '/metrics' in resource:
            return 'metrics'
        elif '/users' in resource:
            return 'user'
        elif '/system' in resource:
            return 'system'
        else:
            return 'unknown'
    
    def _generate_compliance_recommendations(self, failed_access: int, critical_events: int) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if failed_access > 10:
            recommendations.append("Review access control policies and implement multi-factor authentication")
        
        if critical_events > 5:
            recommendations.append("Investigate root cause of critical system events")
        
        if failed_access > 5 or critical_events > 2:
            recommendations.append("Schedule security audit and penetration testing")
        
        recommendations.extend([
            "Regular security training for team members",
            "Implement automated security monitoring",
            "Review and update incident response procedures"
        ])
        
        return recommendations

# Global audit logger instance
audit_logger = AuditLogger()
