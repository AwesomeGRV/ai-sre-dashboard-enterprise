terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "ai-sre-demo-rg"
  location = "East US"
}

# Container Registry for Docker images
resource "azurerm_container_registry" "acr" {
  name                = "ai-sre-demo-acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled        = true
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "law" {
  name                = "ai-sre-demo-law"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Application Insights
resource "azurerm_application_insights" "ai" {
  name                = "ai-sre-demo-ai"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  workspace_id        = azurerm_log_analytics_workspace.law.id
  application_type    = "web"
}

# Container App Environment
resource "azurerm_container_app_environment" "cae" {
  name                = "ai-sre-demo-env"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
}

# Sample App Container App
resource "azurerm_container_app" "sample-app" {
  name                         = "sample-app"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"
  
  template {
    min_replicas = 1
    max_replicas = 3
    container {
      name   = "sample-app"
      image  = "${azurerm_container_registry.acr.login_server}/sample-app:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }
  
  ingress {
    external_enabled = true
    target_port     = 3000
    traffic_weight   = 100
  }
}

# Backend API Container App
resource "azurerm_container_app" "backend-api" {
  name                         = "backend-api"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"
  
  template {
    min_replicas = 1
    max_replicas = 3
    container {
      name   = "backend-api"
      image  = "${azurerm_container_registry.acr.login_server}/backend-api:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }
  
  ingress {
    external_enabled = true
    target_port     = 8000
    traffic_weight   = 100
  }
}

# Frontend Dashboard Container App
resource "azurerm_container_app" "frontend" {
  name                         = "frontend"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"
  
  template {
    min_replicas = 1
    max_replicas = 3
    container {
      name   = "frontend"
      image  = "${azurerm_container_registry.acr.login_server}/frontend:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }
  
  ingress {
    external_enabled = true
    target_port     = 3000
    traffic_weight   = 100
  }
}

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = "ai-sre-demo-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Subnet for Container Apps
resource "azurerm_subnet" "container_apps" {
  name                 = "container-apps-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
  delegation {
    name = "Microsoft.App/environments"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

# Update Container App Environment with VNet integration
resource "azurerm_container_app_environment" "cae_vnet" {
  name                = azurerm_container_app_environment.cae.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  
  subnet_id = azurerm_subnet.container_apps.id
}

# Azure Monitor Alert Rules
resource "azurerm_monitor_metric_alert" "high_error_rate" {
  name                = "high-error-rate-alert"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_application_insights.ai.id]
  description         = "Alert when error rate exceeds threshold"
  
  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name    = "exceptions/count"
    aggregation    = "Total"
    operator       = "GreaterThan"
    threshold     = 10
  }
  
  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }
  
  frequency   = "PT1M"
  window_size = "PT5M"
  severity    = 2
}

# Action Group for Alerts
resource "azurerm_monitor_action_group" "email" {
  name                = "ai-sre-demo-alerts"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "ai-sre-alerts"
  
  email_receiver {
    name          = "sre-team"
    email_address = "sre-team@example.com"
  }
}

# Outputs
output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "container_registry_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "sample_app_url" {
  value = "https://${azurerm_container_app.sample-app.latest_fqdn}"
}

output "backend_api_url" {
  value = "https://${azurerm_container_app.backend-api.latest_fqdn}"
}

output "frontend_url" {
  value = "https://${azurerm_container_app.frontend.latest_fqdn}"
}

output "application_insights_app_id" {
  value = azurerm_application_insights.ai.app_id
}
