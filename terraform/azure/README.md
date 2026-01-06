# Azure Terraform Deployment

This directory contains Terraform configuration for deploying the AI-Powered SRE Dashboard to Azure.

## Architecture Overview

The Terraform configuration creates a complete enterprise-grade SRE observability platform on Azure:

### Services Created

1. **Azure Container Apps**
   - `sample-app`: Node.js application with OpenTelemetry instrumentation
   - `backend-api`: FastAPI backend with AI analysis capabilities  
   - `frontend`: React dashboard for single pane of glass view

2. **Azure Container Registry (ACR)**
   - Private Docker registry for storing application images
   - Secure image management and versioning

3. **Azure Monitor Integration**
   - **Log Analytics Workspace**: Centralized log collection and analysis
   - **Application Insights**: Application Performance Monitoring (APM)
   - **Metric Alerts**: Automated alerting for error rates and performance

4. **Networking Infrastructure**
   - **Virtual Network (VNet)**: Isolated network environment
   - **Subnet**: Dedicated subnet for Container Apps with proper delegation
   - **Network Security**: Secure communication between services

## Deployment Steps

### Prerequisites
- Azure CLI installed and configured
- Terraform installed
- Appropriate Azure permissions

### Quick Deploy
```bash
# Navigate to Terraform directory
cd terraform/azure

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply changes
terraform apply
```

### Configuration Options

You can customize the deployment using variables:

```bash
# Custom deployment
terraform apply \
  -var="location=West Europe" \
  -var="resource_group_name=my-sre-rg" \
  -var="alert_email=team@company.com"
```

## Outputs

After deployment, Terraform will output:
- `resource_group_name`: Name of the created resource group
- `container_registry_login_server`: ACR login server for pushing images
- `sample_app_url`: URL of the sample Node.js application
- `backend_api_url`: URL of the FastAPI backend
- `frontend_url`: URL of the React dashboard
- `application_insights_app_id`: App Insights ID for monitoring integration
- `log_analytics_workspace_id`: Log Analytics Workspace ID

## Post-Deployment Steps

1. **Build and Push Docker Images**
```bash
# Tag and push images to ACR
az acr build --registry ai-sre-demo-acr.azurecr.io --image sample-app ./apps/sample-node-app
az acr build --registry ai-sre-demo-acr.azurecr.io --image backend-api ./backend/api
az acr build --registry ai-sre-demo-acr.azurecr.io --image frontend ./frontend/dashboard
```

2. **Configure Monitoring**
- Access Application Insights for detailed performance metrics
- Set up additional alert rules as needed
- Configure Log Analytics queries for custom monitoring

3. **Access Applications**
- Frontend Dashboard: Use the `frontend_url` output
- Backend API: Use the `backend_api_url` output
- Sample App: Use the `sample_app_url` output

## Monitoring and Alerting

The deployment includes:
- **Error Rate Alerts**: Automatic alerts when error rates exceed thresholds
- **Performance Monitoring**: Response time and throughput tracking
- **Log Aggregation**: Centralized logging with Log Analytics
- **Health Monitoring**: Application Insights for real-time health status

## Cost Optimization

- Container Apps use auto-scaling (1-3 replicas)
- Log Analytics retention set to 30 days
- Basic SKU for Container Registry (cost-effective for demos)
- Pay-as-you-go pricing for monitoring services

## Security Features

- Virtual Network isolation
- Private container registry
- Managed identities for Azure services
- Secure communication between services
- RBAC through Azure RBAC (can be extended)

## Cleanup

To remove all resources:
```bash
terraform destroy
```

This deployment provides a production-ready, secure, and scalable SRE observability platform on Azure.
