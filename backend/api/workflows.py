import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """Automated incident response and workflow management"""
    
    def __init__(self):
        self.workflows = {
            "high_severity_incident": {
                "name": "High Severity Incident Response",
                "description": "Automated response for critical incidents",
                "triggers": ["severity:critical", "severity:high"],
                "steps": [
                    {
                        "name": "immediate_notification",
                        "action": "send_alert",
                        "target": "on_call_sre",
                        "timeout": 60,
                        "automated": True
                    },
                    {
                        "name": "create_war_room",
                        "action": "create_channel",
                        "target": "slack_war_room",
                        "timeout": 120,
                        "automated": True
                    },
                    {
                        "name": "escalate_management",
                        "action": "send_email",
                        "target": "management",
                        "timeout": 300,
                        "automated": True
                    }
                ],
                "auto_execute": True
            },
            "service_degradation": {
                "name": "Service Degradation Response",
                "description": "Automated response for performance issues",
                "triggers": ["response_time:>1000", "error_rate:>5", "availability:<99"],
                "steps": [
                    {
                        "name": "scale_horizontal",
                        "action": "scale_service",
                        "target": "web_servers",
                        "timeout": 300,
                        "automated": True,
                        "conditions": ["cpu_usage>80", "memory_usage>80"]
                    },
                    {
                        "name": "enable_cache",
                        "action": "configure_cache",
                        "target": "application_cache",
                        "timeout": 180,
                        "automated": True
                    },
                    {
                        "name": "restart_services",
                        "action": "restart_service",
                        "target": "affected_services",
                        "timeout": 120,
                        "automated": True,
                        "conditions": ["error_rate>10"]
                    }
                ],
                "auto_execute": False
            },
            "database_connectivity": {
                "name": "Database Connectivity Issues",
                "description": "Automated response for database problems",
                "triggers": ["database_error", "connection_timeout"],
                "steps": [
                    {
                        "name": "check_connection_pool",
                        "action": "validate_connections",
                        "target": "database_pool",
                        "timeout": 60,
                        "automated": True
                    },
                    {
                        "name": "failover_to_backup",
                        "action": "switch_database",
                        "target": "backup_database",
                        "timeout": 180,
                        "automated": True,
                        "conditions": ["primary_db_unavailable"]
                    },
                    {
                        "name": "restart_database_service",
                        "action": "restart_service",
                        "target": "database_service",
                        "timeout": 120,
                        "automated": True
                    }
                ],
                "auto_execute": False
            },
            "security_incident": {
                "name": "Security Incident Response",
                "description": "Automated response for security events",
                "triggers": ["security_breach", "unauthorized_access", "malware_detected"],
                "steps": [
                    {
                        "name": "isolate_affected_systems",
                        "action": "isolate_system",
                        "target": "compromised_hosts",
                        "timeout": 300,
                        "automated": True
                    },
                    {
                        "name": "block_malicious_ips",
                        "action": "block_ip",
                        "target": "firewall",
                        "timeout": 60,
                        "automated": True
                    },
                    {
                        "name": "rotate_credentials",
                        "action": "rotate_passwords",
                        "target": "affected_accounts",
                        "timeout": 120,
                        "automated": True
                    },
                    {
                        "name": "security_scan",
                        "action": "security_scan",
                        "target": "affected_systems",
                        "timeout": 600,
                        "automated": True
                    }
                ],
                "auto_execute": True
            }
        }
        
        self.active_workflow_runs = []
        self.workflow_history = []
    
    def trigger_workflow(self, workflow_name: str, incident_data: Dict[str, Any], 
                     trigger_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger automated workflow"""
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {"error": f"Workflow {workflow_name} not found"}
        
        # Check if workflow should auto-execute
        if not workflow.get("auto_execute", False):
            return {"error": "Workflow requires manual execution"}
        
        # Create workflow run
        workflow_run = {
            "id": f"workflow_{len(self.active_workflow_runs) + 1}",
            "workflow_name": workflow_name,
            "incident_id": incident_data.get("id"),
            "trigger_data": trigger_data or {},
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "current_step": 0
        }
        
        self.active_workflow_runs.append(workflow_run)
        logger.info(f"Workflow {workflow_name} triggered for incident {incident_data.get('id')}")
        
        # Execute workflow steps asynchronously
        asyncio.create_task(self._execute_workflow(workflow_run, workflow, incident_data))
        
        return {
            "workflow_id": workflow_run["id"],
            "status": "triggered",
            "message": f"Workflow {workflow_name} execution started"
        }
    
    async def _execute_workflow(self, workflow_run: Dict[str, Any], workflow: Dict[str, Any], 
                          incident_data: Dict[str, Any]) -> None:
        """Execute workflow steps"""
        steps = workflow.get("steps", [])
        
        for i, step in enumerate(steps):
            try:
                workflow_run["current_step"] = i
                step_result = await self._execute_step(step, incident_data)
                
                workflow_run["steps"].append({
                    "step_name": step["name"],
                    "action": step["action"],
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "result": step_result
                })
                
                # Check timeout
                if "timeout" in step:
                    await asyncio.sleep(step["timeout"])
                
                logger.info(f"Workflow step {step['name']} completed")
                
            except Exception as e:
                workflow_run["steps"].append({
                    "step_name": step["name"],
                    "action": step["action"],
                    "status": "failed",
                    "completed_at": datetime.now().isoformat(),
                    "error": str(e)
                })
                logger.error(f"Workflow step {step['name']} failed: {str(e)}")
        
        # Mark workflow as completed
        workflow_run["status"] = "completed"
        workflow_run["completed_at"] = datetime.now().isoformat()
        
        # Move to history
        self.workflow_history.append(workflow_run)
        self.active_workflow_runs.remove(workflow_run)
        
        logger.info(f"Workflow {workflow_run['workflow_name']} completed")
    
    async def _execute_step(self, step: Dict[str, Any], incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow step"""
        action = step["action"]
        target = step.get("target", "unknown")
        
        # Simulate different actions
        if action == "send_alert":
            return await self._send_alert(target, incident_data)
        elif action == "create_channel":
            return await self._create_communication_channel(target, incident_data)
        elif action == "scale_service":
            return await self._scale_service(target, incident_data)
        elif action == "configure_cache":
            return await self._configure_cache(target, incident_data)
        elif action == "restart_service":
            return await self._restart_service(target, incident_data)
        elif action == "isolate_system":
            return await self._isolate_system(target, incident_data)
        elif action == "block_ip":
            return await self._block_malicious_ips(target, incident_data)
        elif action == "security_scan":
            return await self._perform_security_scan(target, incident_data)
        else:
            return {"action": action, "status": "unknown_action", "target": target}
    
    async def _send_alert(self, target: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert notification"""
        # Simulate sending alert
        await asyncio.sleep(2)  # Simulate API call
        return {
            "action": "alert_sent",
            "target": target,
            "alert_type": "incident_notification",
            "incident_id": incident_data.get("id")
        }
    
    async def _create_communication_channel(self, channel: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create communication channel"""
        await asyncio.sleep(3)  # Simulate channel creation
        return {
            "action": "channel_created",
            "channel": channel,
            "channel_url": f"https://slack.com/channels/{channel}",
            "purpose": "incident_coordination"
        }
    
    async def _scale_service(self, target: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scale service horizontally"""
        await asyncio.sleep(5)  # Simulate scaling operation
        return {
            "action": "service_scaled",
            "target": target,
            "scaling_type": "horizontal",
            "instances_added": 2,
            "new_capacity": "150% of original"
        }
    
    async def _configure_cache(self, target: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure application cache"""
        await asyncio.sleep(2)  # Simulate cache configuration
        return {
            "action": "cache_configured",
            "target": target,
            "cache_type": "redis",
            "ttl": 3600,
            "status": "active"
        }
    
    async def _restart_service(self, target: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restart service"""
        await asyncio.sleep(3)  # Simulate service restart
        return {
            "action": "service_restarted",
            "target": target,
            "restart_time": 15,
            "status": "running"
        }
    
    async def _isolate_system(self, target: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Isolate affected system"""
        await asyncio.sleep(4)  # Simulate isolation
        return {
            "action": "system_isolated",
            "target": target,
            "isolation_type": "network_segmentation",
            "quarantine_status": "active"
        }
    
    async def _block_malicious_ips(self, target: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Block malicious IP addresses"""
        await asyncio.sleep(1)  # Simulate firewall update
        return {
            "action": "ips_blocked",
            "target": target,
            "blocked_ips": ["192.168.1.100", "10.0.0.50"],
            "block_duration": 86400  # 24 hours
        }
    
    async def _perform_security_scan(self, target: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security scan"""
        await asyncio.sleep(10)  # Simulate security scan
        return {
            "action": "security_scan_completed",
            "target": target,
            "scan_type": "vulnerability_assessment",
            "threats_found": 3,
            "scan_duration": 600
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of workflow run"""
        # Check active runs
        for run in self.active_workflow_runs:
            if run["id"] == workflow_id:
                return run
        
        # Check history
        for run in self.workflow_history:
            if run["id"] == workflow_id:
                return run
        
        return {"error": f"Workflow {workflow_id} not found"}
    
    def get_available_workflows(self) -> List[Dict[str, Any]]:
        """Get list of available workflows"""
        return [
            {
                "name": name,
                "description": workflow["description"],
                "triggers": workflow["triggers"],
                "auto_execute": workflow["auto_execute"],
                "step_count": len(workflow["steps"])
            }
            for name, workflow in self.workflows.items()
        ]
    
    def get_workflow_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        return sorted(
            self.workflow_history,
            key=lambda x: x.get("started_at", ""),
            reverse=True
        )[:limit]

# Global workflow engine instance
workflow_engine = WorkflowEngine()
