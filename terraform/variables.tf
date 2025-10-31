variable "resource_group_name" {
  type        = string
  description = "The name of the Azure resource group where all resources will be deployed."
}

variable "resource_group_location" {
  type        = string
  default     = "francecentral"
  description = "The Azure region where the resource group and its resources will be deployed."
}

variable "data_lake_name" {
  type        = string
  description = "The name of the Azure Data Lake Storage account."
}

variable "git_repo_url" {
  type        = string
  description = "URL of the Git repository containing Databricks notebooks"
}