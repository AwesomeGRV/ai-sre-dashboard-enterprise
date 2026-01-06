output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "container_registry_login_server" {
  description = "Login server for Azure Container Registry"
  value       = azurerm_container_registry.acr.login_server
}

output "sample_app_url" {
  description = "URL of the sample application"
  value       = "https://${azurerm_container_app.sample-app.latest_fqdn}"
}

output "backend_api_url" {
  description = "URL of the backend API"
  value       = "https://${azurerm_container_app.backend-api.latest_fqdn}"
}

output "frontend_url" {
  description = "URL of the frontend dashboard"
  value       = "https://${azurerm_container_app.frontend.latest_fqdn}"
}

output "application_insights_app_id" {
  description = "Application Insights ID for monitoring"
  value       = azurerm_application_insights.ai.app_id
}

output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = azurerm_log_analytics_workspace.law.id
}

output "virtual_network_id" {
  description = "Virtual Network ID"
  value       = azurerm_virtual_network.vnet.id
}
