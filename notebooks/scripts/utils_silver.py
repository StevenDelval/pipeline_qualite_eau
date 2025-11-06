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


def transform_com_silver(df: DataFrame) -> DataFrame:
    """
    Transforme le DataFrame Commune Bronze en DataFrame Silver.

    Cette fonction effectue les opérations suivantes :
    1. Renomme les colonnes pour correspondre au schéma Silver.
    2. Convertit les colonnes et met en minuscules certaines valeurs textuelles.
    3. Déduplique les lignes en conservant la ligne la plus récente pour chaque combinaison
       de (cd_reseau, insee_commune, quartier) selon l'année.
    4. Sélectionne uniquement les colonnes finales pertinentes pour la table Silver.

    Args:
        df (DataFrame): DataFrame Spark Bronze contenant les données brutes Commune.

    Returns:
        DataFrame: DataFrame Spark Silver transformé, prêt à être inséré dans la table Delta.
    """

    # Renommer les colonnes pour le schéma Silver
    df = (
        df
        .withColumnRenamed("Inseecommune", "insee_commune")
        .withColumnRenamed("Nomcommune", "nom_commune")
        .withColumnRenamed("Quartier", "quartier")
        .withColumnRenamed("Cdreseau", "cd_reseau")
        .withColumnRenamed("Nomreseau", "nom_reseau")
        .withColumnRenamed("Debutalim", "debut_alim")
    )

    # Convertir les colonnes et enrichissement
    df = (
        df
        .withColumn("quartier", F.lower(F.col("quartier")))      # mettre en minuscules
        .withColumn("debut_alim", F.to_date("debut_alim", "yyyy-MM-dd"))  # convertir en date
    )
    df = df.withColumn("annee", F.col("annee").cast("int"))
    # Déduplication par groupe avec priorité sur l'année la plus récente
   
    window_spec = Window.partitionBy(
        "cd_reseau", "insee_commune", "quartier"
    ).orderBy(
        F.col("annee").desc()
    )

    df = df.withColumn("row_number", F.row_number().over(window_spec)) \
           .filter(F.col("row_number") == 1) \
           .drop("row_number")

    # Sélection des colonnes finales pour Silver
    colonnes_a_garder = [
        "insee_commune",
        "nom_commune",
        "quartier",
        "cd_reseau",
        "nom_reseau",
        "debut_alim",
        "annee",
    ]

    df = df.select([c for c in colonnes_a_garder if c in df.columns])

    return df

def transform_plv_silver(df: DataFrame) -> DataFrame:
    """
    Transforme le DataFrame PLV Bronze pour créer le DataFrame Silver.

    Cette fonction effectue les opérations suivantes :
    1. Renomme les colonnes pour correspondre au schéma Silver.
    2. Convertit les dates et ajoute un timestamp de mise à jour.
    3. Filtre les lignes avec des clés critiques nulles (`cd_reseau` ou `reference_prel`).
    4. Déduplique les lignes en conservant la dernière observation par groupe 
       défini par (cd_reseau, reference_prel, insee_commune_princ, date_prel),
       en se basant sur l'heure la plus récente.
    5. Sélectionne uniquement les colonnes finales pertinentes pour la table Silver.

    Args:
        df (DataFrame): DataFrame Spark Bronze contenant les données brutes PLV.

    Returns:
        DataFrame: DataFrame Spark Silver transformé, prêt à être inséré dans la table Delta.
    """

    
    # Renommer les colonnes pour le schéma Silver
    df = (
        df
        .withColumnRenamed("cddept", "cd_dept")
        .withColumnRenamed("cdreseau", "cd_reseau")
        .withColumnRenamed("referenceprel", "reference_prel")
        .withColumnRenamed("dateprel", "date_prel")
        .withColumnRenamed("heureprel", "heure_prel")
        .withColumnRenamed("inseecommuneprinc", "insee_commune_princ")
        .withColumnRenamed("nomcommuneprinc", "nom_commune_princ")
        .withColumnRenamed("cdreseauamont", "cd_reseau_amont")
        .withColumnRenamed("nomreseauamont", "nom_reseau_amont")
        .withColumnRenamed("pourcentdebit", "pourcent_debit")
        .withColumnRenamed("plvconformitebacterio", "plv_conformite_bacterio")
        .withColumnRenamed("plvconformitechimique", "plv_conformite_chimique")
        .withColumnRenamed("plvconformitereferencebact", "plv_conformite_reference_bact")
        .withColumnRenamed("plvconformitereferencechim", "plv_conformite_reference_chim")
        .withColumnRenamed("conclusionprel", "conclusion_prel")
        .withColumnRenamed("ugelib", "unite_gestion")
        .withColumnRenamed("distrlib", "organisme_exploitant")
        .withColumnRenamed("moalib", "maitre_ouvrage")
    )

    
    # Convertir les colonnes et enrichissement
    df = (
        df
        .withColumn("date_prel", F.to_date("date_prel", "yyyy-MM-dd"))  # Convertir en date Spark
        .withColumn("updated_at", F.current_timestamp())               # Timestamp d'update
    )
    df = df.withColumn("annee", F.col("annee").cast("int"))
    # Filtrer les lignes avec des clés critiques manquantes
    
    df = df.filter(F.col("cd_reseau").isNotNull() & F.col("reference_prel").isNotNull())

    
    # Déduplication par groupe avec priorité sur l'heure la plus récente
    
    window_spec = Window.partitionBy(
        "cd_reseau", "reference_prel", "insee_commune_princ", "date_prel"
    ).orderBy(
        F.desc("heure_prel")  # La dernière observation par heure
    )

    df = df.withColumn("row_number", F.row_number().over(window_spec)) \
           .filter(F.col("row_number") == 1) \
           .drop("row_number")

    
    # Sélection des colonnes finales pour Silver
    
    colonnes_a_garder = [
        "cd_dept",
        "cd_reseau",
        "reference_prel",
        "date_prel",
        "heure_prel",
        "insee_commune_princ",
        "nom_commune_princ",
        "cd_reseau_amont",
        "nom_reseau_amont",
        "pourcent_debit",
        "plv_conformite_bacterio",
        "plv_conformite_chimique",
        "plv_conformite_reference_bact",
        "plv_conformite_reference_chim",
        "conclusion_prel",
        "unite_gestion",
        "organisme_exploitant",
        "maitre_ouvrage",
        "updated_at",
        "annee"
    ]

    df = df.select([c for c in colonnes_a_garder if c in df.columns])
    return df


def transform_result_silver(df: DataFrame) -> DataFrame:
    """
    Transforme le DataFrame Resultats Bronze en DataFrame Silver avec déduplication sur l'année.

    Cette fonction effectue les opérations suivantes :
    1. Renomme les colonnes pour correspondre au schéma Silver.
    2. Ajoute un timestamp `updated_at` pour savoir quand la ligne a été transformée.
    3. Convertit les valeurs "O"/"N" de la colonne `is_qualitatif` en booléen True/False.
    4. Déduplique les lignes en conservant uniquement la ligne la plus récente selon `annee`
       pour chaque combinaison (cd_dept, reference_prel, cd_parametre).
    5. Sélectionne uniquement les colonnes finales pertinentes pour la table Silver.

    Args:
        df (DataFrame): DataFrame Spark Bronze contenant les résultats bruts.

    Returns:
        DataFrame: DataFrame Spark Silver transformé, prêt à être inséré dans la table Delta.
    """

    
    # Renommer les colonnes pour le schéma Silver
    
    df = (
        df
        .withColumnRenamed("cddept", "cd_dept")
        .withColumnRenamed("referenceprel", "reference_prel")
        .withColumnRenamed("cdparametresiseeaux", "cd_parametre_sise_eaux")
        .withColumnRenamed("cdparametre", "cd_parametre")
        .withColumnRenamed("libminparametre", "lib_parametre")
        .withColumnRenamed("qualitparam", "is_qualitatif")
        .withColumnRenamed("insituana", "is_labo")
        .withColumnRenamed("rqana", "resultat_analyse")
        .withColumnRenamed("cdunitereferencesiseeaux", "cd_unite_reference_sise_eaux")
        .withColumnRenamed("cdunitereference", "cd_unite_reference")
        .withColumnRenamed("limitequal", "limite_qualite")
        .withColumnRenamed("refqual", "ref_qualite")
        .withColumnRenamed("valtraduite", "val_traduite")
        .withColumnRenamed("casparam", "cd_cas_param")
        .withColumnRenamed("referenceanl", "cd_ana_labo")
    )

    
    # Ajouter un timestamp d'update
    
    df = df.withColumn("updated_at", F.current_timestamp())

    
    # Transformer "O"/"N" en True/False
    
    df = df.withColumn(
        "is_qualitatif",
        F.when(F.upper(F.col("is_qualitatif")) == "O", F.lit(True))
         .when(F.upper(F.col("is_qualitatif")) == "N", F.lit(False))
         .otherwise(F.lit(None))
    )
    # Transformer "L"/"T" en True/False
    
    df = df.withColumn(
        "is_labo",
        F.when(F.upper(F.col("is_labo")) == "L", F.lit(True))
         .when(F.upper(F.col("is_labo")) == "T", F.lit(False))
         .otherwise(F.lit(None))
    )

    # Nettoyage colonne ref_qualite
    ## Nettoyage de base 
    df = df.withColumn("ref_qualite", F.trim(F.lower(F.col("ref_qualite"))))
    df = df.withColumn("ref_qualite", F.regexp_replace("ref_qualite", ",", "."))
    ## Extraction des valeurs
    df = df.withColumn("min_val_ref", F.regexp_extract(F.col("ref_qualite"), r">=\s*([\d\.]+)", 1))
    df = df.withColumn("max_val_ref", F.regexp_extract(F.col("ref_qualite"), r"<=\s*([\d\.]+)", 1))
    ## Nettoyage et normalisation
    df = df.withColumn("min_val_ref", F.when(F.col("min_val_ref") != "", F.col("min_val_ref").cast("double")))
    df = df.withColumn("max_val_ref", F.when(F.col("max_val_ref") != "", F.col("max_val_ref").cast("double")))

    # Nettoyage colonne limite_qualite
    ## Nettoyage de base 
    df = df.withColumn("limite_qualite", F.trim(F.lower(F.col("limite_qualite"))))
    df = df.withColumn("limite_qualite", F.regexp_replace("limite_qualite", ",", "."))
     ## Extraction des valeurs
    df = df.withColumn("valeur_limite", F.regexp_extract(F.col("limite_qualite"), r"<=\s*([\d\.]+)", 1))
    ## Nettoyage et normalisation
    df = df.withColumn("valeur_limite", F.when(F.col("valeur_limite") != "", F.col("valeur_limite").cast("double")))

    # Nettoyage valeur resultat
    df = df.withColumn("cd_unite_reference_sise_eaux", F.trim(F.lower(F.col("cd_unite_reference_sise_eaux"))))

    df = df.withColumn(
        "val_finale",
        when(F.col("cd_unite_reference_sise_eaux") == "sans objet", F.col("resultat_analyse"))
        .otherwise(F.col("val_traduite"))
    )


    # Déduplication par année la plus récente
    
    window_spec = Window.partitionBy("cd_dept", "reference_prel", "cd_parametre") \
                        .orderBy(F.col("annee").desc())

    df = df.withColumn("row_number", F.row_number().over(window_spec)) \
           .filter(F.col("row_number") == 1) \
           .drop("row_number")

    
    # Sélection des colonnes finales pour Silver
    
    colonnes_a_garder = [
        "cd_dept",
        "reference_prel",
        "cd_parametre_sise_eaux",
        "cd_parametre",
        "lib_parametre",
        "is_qualitatif",
        "is_labo",
        "resultat_analyse",
        "cd_unite_reference_sise_eaux",
        "cd_unite_reference",
        "min_val_ref",
        "max_val_ref",
        "valeur_limite",
        "val_traduite",
        "val_finale",
        "cd_cas_param",
        "cd_ana_labo",
        "updated_at",
        "annee"
    ]

    df = df.select([c for c in colonnes_a_garder if c in df.columns])

    return df