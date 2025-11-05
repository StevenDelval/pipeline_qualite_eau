import logging
from databricks.sdk.runtime import *

def write_df_to_parquet(df, 
    path: str,
    logger: logging.Logger, 
    mode: str = "overwrite"
):
    """
    Écrit un DataFrame Spark en format Parquet dans le Data Lake.

    Args:
        df (DataFrame): Le DataFrame Spark à écrire.
        path (str): Chemin complet dans le Data Lake (ex: '/mnt/datalake/bronze/dis_plv/').
        logger (logging.Logger): Logger Python pour suivre les actions.
        mode (str): Mode d’écriture ('overwrite', 'append', etc.).
    """
    try:
        if df.isEmpty():
            logger.warning(f"Aucune donnée à écrire dans {path}.")
            return

        logger.info(f"Écriture en Parquet dans {path} (mode={mode})...")
        df.write.mode(mode).parquet(path)
        logger.info(f"Données stockées avec succès dans {path}")

    except Exception as e:
        logger.error(f"Erreur écriture Parquet dans {path}: {e}", exc_info=True)