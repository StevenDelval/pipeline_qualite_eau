resource "azurerm_resource_group" "resource_group" {
  location = var.resource_group_location
  name     = var.resource_group_name
}

resource "azurerm_storage_account" "data_lake" {
  name                     = var.data_lake_name
  resource_group_name      = var.resource_group_name
  location                 = var.resource_group_location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  access_tier              = "Cool" 
  is_hns_enabled           = true
}

resource "azurerm_storage_data_lake_gen2_filesystem" "data_lake_filesystem" {
  name               = "donnees-qualite-eau"
  storage_account_id = azurerm_storage_account.data_lake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "data_lake_filesystem_bronze" {
  name               = "donnees-qualite-eau-bronze"
  storage_account_id = azurerm_storage_account.data_lake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "data_lake_filesystem_silver" {
  name               = "donnees-qualite-eau-silver"
  storage_account_id = azurerm_storage_account.data_lake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "data_lake_filesystem_gold" {
  name               = "donnees-qualite-eau-gold"
  storage_account_id = azurerm_storage_account.data_lake.id
}