import logging
from databricks.sdk.runtime import *

def ensure_mount(
    mount_point: str,
    container_name: str,
    secret_scope_name: str,
    secret_key_name: str,
    storage_account_name: str,
    logger: logging.Logger
):
    """
    Vérifie si un point de montage Databricks existe, et le crée si nécessaire.
    
    Args:
        mount_point (str): Chemin du point de montage local dans Databricks (ex: '/mnt/datalake').
        container_name (str): Nom du conteneur Blob Storage à monter.
        secret_scope_name (str): Nom du scope Databricks contenant le secret.
        secret_key_name (str): Nom de la clé secret contenant la clé du storage.
        storage_account_name (str): Nom du compte de stockage Azure.
        logger (logging.Logger): Logger Python pour suivre les actions.

    Raises:
        Exception: Si la création du montage échoue.
    """
    try:
        # Récupérer les points de montage existants
        mounts = [m.mountPoint for m in dbutils.fs.mounts()]
        if mount_point in mounts:
            logger.info(f"Mount already exists: {mount_point}")
            return

        # Récupérer la clé de stockage depuis Databricks Secrets
        storage_key = dbutils.secrets.get(scope=secret_scope_name, key=secret_key_name)

        configs = {
            f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net": storage_key
        }

        # Créer le mount
        dbutils.fs.mount(
            source=f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/",
            mount_point=mount_point,
            extra_configs=configs
        )

        
        logger.info(f"Mount created successfully at {mount_point}")

    except Exception as e:

        logger.error(f"Failed to ensure mount: {e}", exc_info=True)
        raise
