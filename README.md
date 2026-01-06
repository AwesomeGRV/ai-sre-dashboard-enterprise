# AI‑Powered Application Health & Availability Dashboard

## Overview
This project demonstrates an **enterprise‑grade SRE observability platform**
that provides a **single pane of glass** for application availability, reliability,
and operational intelligence using **OpenTelemetry, Prometheus, Grafana, and AI**.

The solution mimics how modern SRE teams design internal reliability platforms
or Copilot‑style tools to:
- Monitor application health
- Detect incidents
- Explain failures using AI
- Improve MTTR

---

##  Key Capabilities
- **End‑to‑end observability** (metrics, traces, logs)
- **Application availability & SLA indicators**
- **Prometheus‑based metrics storage**
- **Grafana dashboards**
- **AI‑generated incident summaries & RCA**
- **Docker‑based local demo**
- **Azure‑ready deployment via Terraform**
- **Real‑time React dashboard** with modern UI

---

##  Prerequisites

Before running this demo, ensure you have:

1. **Docker & Docker Compose** (recommended for local demo)
   ```bash
   # Install Docker Desktop for Windows/Mac
   # Or install Docker Engine for Linux
   ```

2. **Node.js 18+** (for manual development)
3. **Python 3.11+** (for backend development)

---

##  Architecture

```
React Dashboard (Single Pane of Glass)    :3001
        |
 Backend API (FastAPI + AI Analysis)    :8000
        |
 ├── Prometheus (Metrics Storage)       :9090
 ├── Grafana (Visualization)            :3002
 ├── OTel Collector                     :4317/4318
 |
 Sample Node.js App (Instrumented)       :3000
        |
 OpenTelemetry SDK
```

---

##  Quick Start (Local Demo)

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate to the project
git clone <your-repo-url>
cd ai-sre-dashboard-enterprise

# Start all services
docker compose up -d --build

# Wait for services to start (2-3 minutes)
docker compose logs -f
```

### Option 2: Manual Development Setup

```bash
# Terminal 1: Start Sample App
cd apps/sample-node-app
npm install
npm start

# Terminal 2: Start Backend API
cd backend/api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start Frontend
cd frontend/dashboard
npm install
npm start

# Terminal 4: Start Observability Stack
docker compose up -d prometheus grafana otel
```

---

##  Access Points

Once running, access the dashboard at:

- ** Main Dashboard**: http://localhost:3001
- ** Backend API**: http://localhost:8000
- ** Sample App**: http://localhost:3000
- ** Prometheus**: http://localhost:9090
- ** Grafana**: http://localhost:3002 (admin/admin)
- ** OTel Collector**: http://localhost:4318

---

##  Demo Features

### 1. **System Health Overview**
- Real-time service status
- Health check monitoring
- Service dependency visualization

### 2. **Performance Metrics**
- Request count and error rates
- Response time trends
- System uptime tracking

### 3. **AI-Powered Incident Analysis**
- Automatic incident detection
- AI-generated root cause analysis
- MTTR optimization suggestions

### 4. **SLA Monitoring**
- Availability percentage tracking
- SLA compliance indicators
- Downtime calculation

---

##  Interactive Demo Steps

1. **Generate Demo Incidents**
   - Click "Generate Demo Incidents" button
   - Watch incidents appear with different severities

2. **AI Analysis**
   - Click "Generate Analysis" on any incident
   - View AI-powered insights and recommendations

3. **Monitor Metrics**
   - Watch real-time performance charts
   - Observe response time trends

4. **SLA Tracking**
   - Monitor availability percentages
   - Check SLA compliance status

---

##  Testing the System

### Generate Load
```bash
# Generate traffic to the sample app
curl -X POST http://localhost:3000/api/load -H "Content-Type: application/json" -d '{"intensity": "high"}'

# Check health status
curl http://localhost:3000/health

# View metrics
curl http://localhost:3000/metrics
```

### API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get metrics
curl http://localhost:8000/metrics

# Get incidents
curl http://localhost:8000/incidents

# Generate demo incidents
curl -X POST http://localhost:8000/demo/generate-incidents

# Get SLA data
curl http://localhost:8000/sla
```

---

##  AI Integration

The system uses AI to provide:

- **Incident Summarization**: Automatic generation of incident descriptions
- **Root Cause Analysis**: AI-powered identification of potential causes
- **MTTR Optimization**: Suggestions for reducing mean time to resolution
- **Correlation Analysis**: Links between errors, latency, and traffic patterns

*Note: Current implementation uses simulated AI responses. Integration with OpenAI or other AI services can be added by configuring API keys in the backend.*

---

##  Azure Deployment

### Terraform Deployment
```bash
cd terraform/azure
terraform init
terraform plan
terraform apply
```

### Azure Services Deployed:
- **Azure Container Apps** (for microservices)
- **Azure Monitor** (for metrics and logs)
- **Application Insights** (for APM)
- **Azure Container Registry** (for images)
- **Virtual Network** (for secure connectivity)

---

##  Project Structure

```
ai-sre-dashboard-enterprise/
├── apps/
│   └── sample-node-app/          # Instrumented Node.js application
├── backend/
│   └── api/                      # FastAPI backend with AI analysis
├── frontend/
│   └── dashboard/                # React dashboard UI
├── otel/
│   └── collector.yaml            # OpenTelemetry collector config
├── prometheus/
│   └── prometheus.yml            # Prometheus configuration
├── terraform/
│   └── azure/                    # Azure deployment templates
├── docs/
│   ├── ai-prompts.md             # AI prompt templates
│   └── demo-script.md            # Demo walkthrough
├── docker-compose.yml            # Local development setup
└── README.md                      # This file
```

---

##  Configuration

### Environment Variables
```bash
# Backend API
REACT_APP_API_URL=http://localhost:8000

# OpenAI Integration (Optional)
OPENAI_API_KEY=your_api_key_here
```

### Customization
- Modify `apps/sample-node-app/server.js` to change application behavior
- Update `backend/api/main.py` to add new AI analysis features
- Customize `frontend/dashboard/src/` components for UI changes

---

##  Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check logs
   docker compose logs <service-name>
   
   # Restart services
   docker compose down && docker compose up -d
   ```

2. **Frontend not connecting to backend**
   - Verify backend is running on port 8000
   - Check CORS settings in backend

3. **Metrics not appearing**
   - Verify OpenTelemetry collector is running
   - Check Prometheus targets: http://localhost:9090/targets

4. **Port conflicts**
   - Modify ports in `docker-compose.yml`
   - Ensure no other services are using the same ports

---

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

---

##  Why This Project Matters

This repo demonstrates **real SRE problem‑solving**, not just dashboards.
It aligns with modern **Azure SRE Agent / Copilot** patterns and provides:

- **Production-ready observability stack**
- **AI-powered operational intelligence**
- **Enterprise-grade architecture**
- **Cloud-native deployment patterns**
- **Real-world SRE scenarios**

Perfect for:
- SRE teams learning observability
- DevOps engineers implementing monitoring
- Platform architects designing reliability systems
- Anyone interested in AI for operations

---

##  Support

For questions or issues:
1. Check the troubleshooting section
2. Review the demo documentation in `docs/`
3. Open an issue on GitHub

---

** Ready to deploy? Your AI-Powered SRE Dashboard is now complete!**

