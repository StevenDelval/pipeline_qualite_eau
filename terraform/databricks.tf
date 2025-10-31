resource "azurerm_databricks_workspace" "databricks_workspace" {
  name                = "adw-qualite-eaux-traitement"
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = azurerm_resource_group.resource_group.location
  sku                 = "standard"
}

resource "databricks_cluster" "cluster" {
  cluster_name            = "cluster"
  spark_version           = "13.3.x-scala2.12"
  node_type_id            = "Standard_DS3_v2"
  autotermination_minutes = 30
  spark_env_vars = {
    "STORAGE_ACCOUNT_NAME":azurerm_storage_account.data_lake.name,
    "SECRET_SCOPE_NAME": databricks_secret_scope.datalake_scope.name,
    "SECRET_KEY_NAME": databricks_secret.datalake_key.key,
    "CONTAINER_NAME":azurerm_storage_data_lake_gen2_filesystem.data_lake_filesystem.name,
    "CONTAINER_BRONZE":azurerm_storage_data_lake_gen2_filesystem.data_lake_filesystem_bronze.name,
    "CONTAINER_SILVER":azurerm_storage_data_lake_gen2_filesystem.data_lake_filesystem_silver.name,
    "CONTAINER_GOLD":azurerm_storage_data_lake_gen2_filesystem.data_lake_filesystem_gold.name,
  }

  autoscale {
    min_workers = 1
    max_workers = 5
  }

}

resource "databricks_secret_scope" "datalake_scope" {
  name = "datalake-scope"
  initial_manage_principal = "users"
}

resource "databricks_secret" "datalake_key" {
  key          = "storage-account-key"
  string_value = azurerm_storage_account.data_lake.primary_access_key
  scope        = databricks_secret_scope.datalake_scope.name
}

resource "databricks_library" "datalake_sdk" {
  cluster_id = databricks_cluster.cluster.id
  pypi {
    package = "azure-storage-file-datalake"
  }
}

resource "databricks_repo" "git_repo" {
  url    = var.git_repo_url
  path   = "/Repos/repo_git/qualite_eaux"
  branch = "develop"
}