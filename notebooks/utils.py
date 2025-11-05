import logging
import io
from azure.storage.filedatalake import DataLakeServiceClient

class DataLakeLogHandler(logging.Handler):
    """
    Handler personnalisé pour Python logging.
    Chaque message de log est envoyé dans un fichier Azure Data Lake Gen2.

    Paramètres :
    - account_name : str, nom du compte de stockage Azure
    - account_key : str, clé d'accès au compte
    - filesystem_name : str, nom du conteneur / filesystem
    - log_path : str, chemin complet du fichier log dans le Data Lake
    """
    def __init__(self, account_name: str, account_key: str, filesystem_name: str, log_path: str) -> None:
        super().__init__()
        self.service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=account_key
        )
        self.filesystem_client = self.service_client.get_file_system_client(file_system=filesystem_name)
        self.log_path = log_path

        # Crée le fichier si besoin
        self.file_client = self.filesystem_client.get_file_client(self.log_path)
        try:
            self.file_client.get_file_properties()
        except:
            self.file_client.create_file()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Méthode appelée automatiquement par Python logging à chaque log.
        Formate le message, convertit en bytes et l'envoie à la fin du fichier
        Data Lake.
        """
        try:
            msg = self.format(record) + "\n"
            data_bytes = msg.encode("utf-8")
            data = io.BytesIO(data_bytes)

            props = self.file_client.get_file_properties()
            offset = props.size

            self.file_client.append_data(data=data, offset=offset, length=len(data_bytes))
            self.file_client.flush_data(offset + len(data_bytes))
        except Exception as e:
            print(f"Erreur d’envoi du log : {e}")


def get_datalake_logger(
    logger_name: str,
    account_name: str,
    account_key: str,
    filesystem_name: str,
    log_path: str,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Crée et configure un logger Python pour envoyer les logs vers Azure Data Lake.

    Paramètres :
    - logger_name : str, nom du logger (permet d'utiliser plusieurs loggers distincts)
    - account_name : str, nom du compte Azure Storage
    - account_key : str, clé d'accès
    - filesystem_name : str, nom du conteneur / filesystem
    - log_path : str, chemin complet du fichier log dans le Data Lake
    - level : logging level (par défaut logging.INFO)

    Retour :
    - logger configuré prêt à l'emploi

    Notes :
    - La fonction vérifie si le logger a déjà un DataLakeLogHandler pour éviter
      les doublons.
    - Chaque log est envoyé en continu dans le fichier Data Lake sans écraser
      les précédents messages.
    """
    logger = logging.getLogger(logger_name)

    # Supprime tous les handlers existants
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Ajoute le DataLakeLogHandler
    handler = DataLakeLogHandler(account_name, account_key, filesystem_name, log_path)
    formatter = logging.Formatter('%(asctime)s,%(levelname)s,"%(message)s"')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(level)
    return logger