from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import json
import random
from datetime import datetime, timedelta
import os
import logging
from ai_engine import ai_engine
from alerting import alert_manager
from audit import audit_logger
from analytics import analytics_engine
from auth import rbac_manager
from workflows import workflow_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SRE Dashboard API", version="2.0.0")

# Security
security = HTTPBearer(auto_error=False)

# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: Dict[str, str]):
    """Authenticate user and return session token"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    auth_result = rbac_manager.authenticate(username, password)
    if not auth_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Log successful login
    audit_logger.log_user_action(
        user_id=username,
        action="login",
        resource="authentication",
        details={"success": True}
    )
    
    return auth_result

@app.post("/auth/logout")
async def logout(session_data: Dict[str, str]):
    """Logout user and invalidate session"""
    session_token = session_data.get("session_token")
    success = rbac_manager.logout(session_token)
    
    if success:
        # Log logout
        session = rbac_manager.validate_session(session_token)
        if session:
            audit_logger.log_user_action(
                user_id=session.get("username"),
                action="logout",
                resource="authentication",
                details={"success": True}
            )
    
    return {"message": "Logged out successfully"}

@app.get("/auth/me")
async def get_current_user(session_data: Dict[str, str]):
    """Get current user information"""
    session_token = session_data.get("session_token")
    user_info = rbac_manager.get_user_info(session_token)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return user_info

# RBAC-protected endpoints
def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(session_data: Dict[str, str], *args, **kwargs):
            session_token = session_data.get("session_token")
            if not rbac_manager.has_permission(session_token, permission):
                raise HTTPException(status_code=403, detail=f"Permission required: {permission}")
            return await func(session_data, *args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str):
    """Decorator to require specific role"""
    def decorator(func):
        async def wrapper(session_data: Dict[str, str], *args, **kwargs):
            session_token = session_data.get("session_token")
            if not rbac_manager.has_role(session_token, role):
                raise HTTPException(status_code=403, detail=f"Role required: {role}")
            return await func(session_data, *args, **kwargs)
        return wrapper
    return decorator

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session validation middleware
@app.middleware("http")
async def add_session_token(request, call_next):
    """Add session token validation to requests"""
    # Skip auth for login endpoint
    if request.url.path.startswith("/auth/"):
        response = await call_next(request)
        return response
    
    # Check for session token in headers
    session_token = request.headers.get("X-Session-Token")
    if not session_token:
        session_token = request.query_params.get("session_token")
    
    if session_token:
        # Validate session
        session = rbac_manager.validate_session(session_token)
        if session:
            request.state.session = session
        else:
            request.state.session = None
    
    response = await call_next(request)
    return response

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, Any]

class Incident(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    created_at: str
    resolved_at: Optional[str] = None
    description: str
    ai_analysis: Optional[str] = None

class MetricsData(BaseModel):
    timestamp: str
    request_count: int
    error_count: int
    response_time_avg: float
    uptime: int

# In-memory storage for demo
incidents_db = []
metrics_history = []

@app.get("/")
async def root():
    return {"message": "SRE Dashboard API is running"}

@app.get("/health", response_model=HealthStatus)
async def get_health_status():
    """Get overall system health status"""
    try:
        # Check sample app health
        app_response = requests.get("http://app:3000/health", timeout=5)
        app_healthy = app_response.status_code == 200
    except:
        app_healthy = False
    
    # Check Prometheus health
    try:
        prom_response = requests.get("http://prometheus:9090/-/healthy", timeout=5)
        prom_healthy = prom_response.status_code == 200
    except:
        prom_healthy = False
    
    overall_status = "healthy" if app_healthy and prom_healthy else "degraded"
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        services={
            "sample_app": {"status": "healthy" if app_healthy else "unhealthy", "url": "http://app:3000"},
            "prometheus": {"status": "healthy" if prom_healthy else "unhealthy", "url": "http://prometheus:9090"},
            "otel_collector": {"status": "healthy", "url": "http://otel:4317"}
        }
    )

@app.get("/alerts", response_model=List[Dict[str, Any]])
async def get_alerts():
    """Get all active alerts"""
    return alert_manager.get_active_alerts()

@app.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    success = alert_manager.acknowledge_alert(alert_id)
    if success:
        # Log alert acknowledgment for audit
        audit_logger.log_user_action(
            user_id="system",
            action="alert_acknowledged",
            resource=f"/alerts/{alert_id}",
            details={"alert_id": alert_id}
        )
        
        return {"message": f"Alert {alert_id} acknowledged", "status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Alert not found")

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    success = alert_manager.resolve_alert(alert_id)
    if success:
        # Log alert resolution for audit
        audit_logger.log_user_action(
            user_id="system",
            action="alert_resolved",
            resource=f"/alerts/{alert_id}",
            details={"alert_id": alert_id}
        )
        
        return {"message": f"Alert {alert_id} resolved", "status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/audit/logs")
async def get_audit_logs(filters: Dict[str, Any] = None):
    """Get audit logs"""
    return audit_logger.get_audit_logs(filters)

@app.get("/audit/access-logs")
async def get_access_logs(filters: Dict[str, Any] = None):
    """Get access logs"""
    return audit_logger.get_access_logs(filters)

@app.get("/audit/system-events")
async def get_system_events(filters: Dict[str, Any] = None):
    """Get system events"""
    return audit_logger.get_system_events(filters)

@app.get("/audit/compliance-report")
async def get_compliance_report(start_date: str, end_date: str):
    """Generate compliance report"""
    return audit_logger.generate_compliance_report(start_date, end_date)

@app.get("/analytics/performance")
async def get_performance_report(time_range: str = "24h"):
    """Generate performance analytics report"""
    return analytics_engine.generate_performance_report(time_range)

@app.get("/analytics/incidents")
async def get_incident_report(time_range: str = "7d"):
    """Generate incident analytics report"""
    return analytics_engine.generate_incident_report(time_range)

@app.get("/analytics/sla")
async def get_sla_report(time_range: str = "30d"):
    """Generate SLA analytics report"""
    return analytics_engine.generate_sla_report(time_range)

@app.get("/analytics/capacity")
async def get_capacity_planning_report():
    """Generate capacity planning report"""
    return analytics_engine.generate_capacity_planning_report()

@app.get("/workflows")
@require_permission("incidents:read")
async def get_available_workflows():
    """Get available automated workflows"""
    return workflow_engine.get_available_workflows()

@app.post("/workflows/{workflow_name}/trigger")
@require_permission("incidents:update")
async def trigger_workflow(workflow_name: str, incident_id: str, request: Request):
    """Trigger automated workflow for incident"""
    # Get incident data
    incident = next((i for i in incidents_db if i.id == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Trigger workflow
    trigger_data = {
        "triggered_by": request.state.session.get("username", "system"),
        "triggered_at": datetime.now().isoformat()
    }
    
    result = workflow_engine.trigger_workflow(workflow_name, incident.dict(), trigger_data)
    
    # Log workflow trigger
    audit_logger.log_user_action(
        user_id=request.state.session.get("username", "system"),
        action="workflow_triggered",
        resource=f"workflows/{workflow_name}",
        details={
            "workflow_name": workflow_name,
            "incident_id": incident_id,
            "trigger_data": trigger_data
        }
    )
    
    return result

@app.get("/workflows/{workflow_id}/status")
@require_permission("incidents:read")
async def get_workflow_status(workflow_id: str):
    """Get workflow execution status"""
    return workflow_engine.get_workflow_status(workflow_id)

@app.get("/analytics/dashboard")
@require_permission("analytics:read")
async def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    return {
        "performance_summary": analytics_engine.generate_performance_report("24h"),
        "incident_summary": analytics_engine.generate_incident_report("7d"),
        "sla_summary": analytics_engine.generate_sla_report("30d"),
        "capacity_recommendations": analytics_engine.generate_capacity_planning_report(),
        "generated_at": datetime.now().isoformat()
    }

@app.get("/workflows/history")
@require_permission("incidents:read")
async def get_workflow_history(limit: int = 50):
    """Get workflow execution history"""
    return workflow_engine.get_workflow_history(limit)

@app.get("/metrics")
@require_permission("metrics:read")
async def get_metrics():
    """Get metrics from Prometheus and evaluate alerts"""
    try:
        # Get request count
        response = requests.get(
            "http://prometheus:9090/api/v1/query",
            params={"query": "http_requests_total"},
            timeout=5
        )
        request_count = int(response.json()["data"]["result"][0]["value"][1]) if response.json()["data"]["result"] else 0
        
        # Get error count
        response = requests.get(
            "http://prometheus:9090/api/v1/query",
            params={"query": "http_errors_total"},
            timeout=5
        )
        error_count = int(response.json()["data"]["result"][0]["value"][1]) if response.json()["data"]["result"] else 0
        
        # Get average response time
        response = requests.get(
            "http://prometheus:9090/api/v1/query",
            params={"query": "http_response_time_avg"},
            timeout=5
        )
        response_time = float(response.json()["data"]["result"][0]["value"][1]) if response.json()["data"]["result"] else 0.0
        
        # Get uptime
        response = requests.get(
            "http://prometheus:9090/api/v1/query",
            params={"query": "app_uptime"},
            timeout=5
        )
        uptime = int(response.json()["data"]["result"][0]["value"][1]) if response.json()["data"]["result"] else 0
        
        # Calculate derived metrics
        error_rate = (error_count / max(request_count, 1)) * 100
        availability = max(0, (100 - error_rate))
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "request_count": request_count,
            "error_count": error_count,
            "response_time_avg": response_time,
            "uptime": uptime,
            "error_rate": error_rate,
            "availability_percentage": availability
        }
        
        # Store in history and add to analytics engine
        metrics_history.append(metrics)
        if len(metrics_history) > 100:
            metrics_history.pop(0)
        
        analytics_engine.add_metrics_data(metrics)
        
        # Evaluate alert rules
        triggered_alerts = alert_manager.evaluate_metrics(metrics)
        
        return {
            "metrics": metrics,
            "triggered_alerts": triggered_alerts,
            "total_active_alerts": len(alert_manager.get_active_alerts())
        }
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return []

@app.get("/incidents", response_model=List[Incident])
async def get_incidents():
    """Get all incidents"""
    return incidents_db

@app.post("/incidents", response_model=Incident)
@require_permission("incidents:create")
async def create_incident(incident: Incident, request: Request):
    """Create a new incident"""
    incident.id = str(len(incidents_db) + 1)
    incident.created_at = datetime.now().isoformat()
    incidents_db.append(incident)
    
    # Log incident creation for audit
    audit_logger.log_user_action(
        user_id=request.state.session.get("username", "system"),
        action="created",
        resource="incidents",
        details={"title": incident.title, "severity": incident.severity}
    )
    
    # Add to analytics engine
    analytics_engine.add_incident_data(incident.dict())
    
    return incident

@app.post("/incidents/{incident_id}/analyze")
async def analyze_incident(incident_id: str):
    """Perform advanced AI analysis of incident"""
    incident = next((i for i in incidents_db if i.id == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    try:
        # Use advanced AI engine for analysis
        ai_analysis = ai_engine.analyze_incident(incident.dict())
        
        # Update incident with AI analysis
        incident.ai_analysis = json.dumps(ai_analysis, indent=2)
        
        # Log AI analysis for audit
        audit_logger.log_incident_lifecycle(
            incident_id=incident_id,
            action="ai_analysis_completed",
            details={"confidence_score": ai_analysis.get("confidence_score")}
        )
        
        logger.info(f"Advanced AI analysis completed for incident {incident_id}")
        return {
            "incident_id": incident_id,
            "ai_analysis": ai_analysis,
            "analysis_timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"AI analysis failed for incident {incident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="AI analysis failed")

def generate_ai_analysis(incident: Incident) -> str:
    """Generate AI-powered incident analysis"""
    # This is a mock implementation - replace with actual AI service call
    analyses = [
        f"Root cause analysis for '{incident.title}' indicates a potential service degradation. "
        f"Recommend checking service dependencies and recent deployments. "
        f"Estimated MTTR: 15-30 minutes.",
        
        f"The incident '{incident.title}' shows patterns consistent with resource exhaustion. "
        f"Suggested actions: scale horizontally, check memory usage, review recent traffic spikes. "
        f"Impact assessment: Medium severity affecting ~20% of users.",
        
        f"Analysis of '{incident.title}' suggests external dependency failure. "
        f"Immediate action: Implement circuit breaker pattern, monitor third-party SLAs. "
        f"Preventive measures: Add retry logic with exponential backoff."
    ]
    
    return random.choice(analyses)

@app.get("/sla")
async def get_sla_metrics():
    """Get SLA and availability metrics"""
    try:
        # Calculate availability based on error rate
        if metrics_history:
            latest_metrics = metrics_history[-1]
            error_rate = latest_metrics.error_count / max(latest_metrics.request_count, 1)
            availability = max(0, (1 - error_rate) * 100)
        else:
            availability = 99.9
        
        return {
            "availability_percentage": availability,
            "sla_target": 99.9,
            "uptime_percentage": availability,
            "downtime_minutes": max(0, (100 - availability) * 0.1),
            "incident_count": len([i for i in incidents_db if i.status == "open"]),
            "mttr_minutes": 25,  # Mock MTTR
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating SLA: {e}")
        return {
            "availability_percentage": 99.9,
            "sla_target": 99.9,
            "uptime_percentage": 99.9,
            "downtime_minutes": 0,
            "incident_count": 0,
            "mttr_minutes": 0,
            "last_updated": datetime.now().isoformat()
        }

@app.post("/demo/generate-incidents")
async def generate_demo_incidents():
    """Generate demo incidents for testing"""
    demo_incidents = [
        {
            "title": "High Response Time Detected",
            "severity": "medium",
            "status": "open",
            "description": "Response times have increased by 200% in the last 5 minutes"
        },
        {
            "title": "Service Unavailability",
            "severity": "high", 
            "status": "open",
            "description": "Sample application is not responding to health checks"
        },
        {
            "title": "Error Rate Spike",
            "severity": "low",
            "status": "resolved",
            "description": "Error rate increased temporarily but has recovered"
        }
    ]
    
    for incident_data in demo_incidents:
        incident = Incident(**incident_data)
        incident.id = str(len(incidents_db) + 1)
        incident.created_at = datetime.now().isoformat()
        if incident.status == "resolved":
            incident.resolved_at = (datetime.now() - timedelta(minutes=30)).isoformat()
        incidents_db.append(incident)
    
    return {"message": f"Generated {len(demo_incidents)} demo incidents"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
