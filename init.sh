#!/bin/bash
set -e  # Quitte le script si une commande échoue

# Activer l'exportation automatique des variables d'environnement
set -o allexport

if [ -f .env ]; then
  source .env
else
  echo "Erreur : fichier .env non trouvé."
  exit 1
fi

set +o allexport

# Création du Resource Group
echo "Création du Resource Group : $RESOURCE_GROUP_NAME"
az group create \
  --name "$RESOURCE_GROUP_NAME" \
  --location "$LOCATION"

# Création du Storage Account
echo "Création du Storage Account : $STORAGE_ACCOUNT_NAME"
az storage account create \
  --name "$STORAGE_ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2 \
  --enable-hierarchical-namespace true  # Optionnel si tu veux HNS pour ADLS Gen2

# Création du container pour le Terraform state
echo "Création du container Terraform state : $TFSTATE_CONTAINER_NAME"
az storage container create \
  --name "$TFSTATE_CONTAINER_NAME" \
  --account-name "$STORAGE_ACCOUNT_NAME"

echo "Resources Azure prêtes pour stocker le Terraform state."