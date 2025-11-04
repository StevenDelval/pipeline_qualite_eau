terraform {

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.89, < 4.0.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.50.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "RG_DELVAL_Qualite_eaux_tfstate"
    storage_account_name = "qetfstatestorage"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

provider "databricks" {
  azure_workspace_resource_id = azurerm_databricks_workspace.databricks_workspace.id
}
