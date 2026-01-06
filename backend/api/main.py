from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import json
import random
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SRE Dashboard API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/metrics", response_model=List[MetricsData])
async def get_metrics():
    """Get metrics from Prometheus"""
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
        
        metrics = MetricsData(
            timestamp=datetime.now().isoformat(),
            request_count=request_count,
            error_count=error_count,
            response_time_avg=response_time,
            uptime=uptime
        )
        
        # Store in history (keep last 100 entries)
        metrics_history.append(metrics)
        if len(metrics_history) > 100:
            metrics_history.pop(0)
        
        return [metrics]
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return []

@app.get("/incidents", response_model=List[Incident])
async def get_incidents():
    """Get all incidents"""
    return incidents_db

@app.post("/incidents", response_model=Incident)
async def create_incident(incident: Incident):
    """Create a new incident"""
    incident.id = str(len(incidents_db) + 1)
    incident.created_at = datetime.now().isoformat()
    incidents_db.append(incident)
    return incident

@app.post("/incidents/{incident_id}/analyze")
async def analyze_incident(incident_id: str):
    """Analyze incident using AI"""
    incident = next((i for i in incidents_db if i.id == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Simulate AI analysis (in real implementation, this would call OpenAI or similar)
    ai_analysis = generate_ai_analysis(incident)
    incident.ai_analysis = ai_analysis
    
    return incident

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
