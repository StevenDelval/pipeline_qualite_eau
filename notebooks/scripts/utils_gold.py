from typing import List, Dict
from pyspark.sql import DataFrame
from pyspark.sql import functions as F, Window
from delta.tables import DeltaTable
import logging

def upsert_table(
    df_silver: DataFrame,
    table_name: str,
    partition_cols: List[str],
    merge_condition: str,
    update_condition: str,
    update_cols: Dict[str, str],
    logger: logging.Logger
) -> None:
    """
    Insert / Update les nouvelles lignes dans une table Delta Silver.
    Si la table n'existe pas, elle est créée avec un partitionnement optionnel.

    Cette fonction effectue un MERGE Delta :
      - insère les lignes nouvelles (non présentes)
      - met à jour les lignes existantes uniquement si la condition d'update est remplie

    Args:
        df_silver (DataFrame): DataFrame Spark contenant les données à insérer ou mettre à jour.
        table_name (str): Nom complet de la table Delta cible (ex: "silver.dis_com_silver").
        partition_cols (List[str]): Liste des colonnes utilisées pour partitionner la table à la création.
        merge_condition (str): Condition SQL pour identifier les lignes correspondantes entre la table et le DataFrame.
        update_condition (str): Condition SQL pour décider si une ligne existante doit être mise à jour.
        update_cols (Dict[str, str]): Dictionnaire {colonne_table: expression_DataFrame} pour spécifier les colonnes à mettre à jour.
        logger (logging.Logger): Logger Python pour suivre les actions.

    Returns:
        None
    """
    spark = df_silver.sparkSession

    # Vérifie si la table existe déjà
    if not spark.catalog.tableExists(table_name):
        logger.info(f"Création de la table Delta : {table_name}")

        writer = (
            df_silver.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
        )

        if partition_cols:
            writer = writer.partitionBy(*partition_cols)

        writer.saveAsTable(table_name)
        logger.info(f"Création de la table Delta : {table_name} terminée")
        return

    # Si la table existe, on fait un MERGE Delta
    logger.info(f"Upsert vers la table {table_name}...")

    delta_table = DeltaTable.forName(spark, table_name)

    (
        delta_table.alias("t")
        .merge(
            df_silver.alias("s"),
            merge_condition,  # condition de correspondance
        )
        .whenNotMatchedInsertAll()  # insère seulement les nouvelles lignes
        .whenMatchedUpdate(
            condition=update_condition,
            set=update_cols
        )
        .execute()
    )
    logger.info(f"Upsert terminé dans {table_name}")