import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from databricks.sdk.runtime import *

def read_txt_files_spark(logger: logging.Logger, mount_point: str, prefix: str, sep: str = ",", header: bool = True):
    """
    Lit tous les fichiers TXT correspondant à un préfixe depuis le dossier monté avec Spark.
    Args:
        logger (logging.Logger): Logger Python pour suivre les actions.
        mount_point (str): Chemin du dossier monté.
        prefix (str): Préfixe des fichiers à lire (ex: '2025_10_').
        sep (str): Séparateur utilisé dans les fichiers TXT (par défaut ',').
        header (bool): Indique si la première ligne contient les noms de colonnes.
    Returns:
        pyspark.sql.DataFrame: DataFrame Spark contenant les données chargées.
    """
    path_pattern = f"{mount_point}/{prefix}*.txt"
    logger.info(f"Debut du traitement pour le préfixe {prefix}")
    try:
        df = (
            spark.read.format("csv")  # 'csv' marche aussi pour les fichiers .txt
            .option("header", str(header).lower())
            .option("inferSchema", "true")
            .option("delimiter", sep)
            .load(path_pattern)
        )

        # Ajouter le nom du fichier source comme colonne
        df = df.withColumn("source_file", F.input_file_name())
        
        df = df.withColumn(
            "annee",
            F.regexp_extract(F.col("source_file"), r"dis-(\d{4})", 1)
        )

        n = df.count()
        logger.info(f"{n} lignes chargées pour le préfixe {prefix}")

        return df

    except Exception as e:
        logger.error(f"Erreur lecture fichiers {path_pattern}: {e}", exc_info=True)
        return spark.createDataFrame([], schema=None)  # DataFrame vide
    
def write_df_to_table(logger: logging.Logger, df, table_name: str, mode: str = "overwrite", partition_col: str = None):
    """
    Écrit un DataFrame Spark dans une table Delta Databricks.
    Permet de partitionner la table par une colonne.

    Args:
        logger (logging.Logger): Logger Python pour suivre les actions.
        df (DataFrame): Le DataFrame Spark à stocker.
        table_name (str): Nom complet de la table cible (ex: 'bronze.txt_table').
        mode (str): Mode d’écriture Spark ('overwrite', 'append', 'ignore', 'error').
        partition_col (str, optional): Nom de la colonne pour partitionner la table (ex: 'annee').

    Returns:
        None
    """
    try:
        if df.isEmpty():
            logger.warning(f"Aucune donnée à écrire dans la table '{table_name}'.")
            return

        logger.info(f"Écriture dans la table Delta '{table_name}' (mode={mode})...")

        writer = df.write.format("delta").mode(mode).option("overwriteSchema", "true")
        if partition_col:
            writer = writer.partitionBy(partition_col)

        writer.saveAsTable(table_name)

        logger.info(f"Données stockées avec succès dans '{table_name}'")

    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans la table '{table_name}': {e}", exc_info=True)