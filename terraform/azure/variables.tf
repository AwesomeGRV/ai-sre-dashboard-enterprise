variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "ai-sre-demo-rg"
}

variable "container_registry_name" {
  description = "Name of the Azure Container Registry"
  type        = string
  default     = "ai-sre-demo-acr"
}

variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
  default     = "sre-team@example.com"
}
