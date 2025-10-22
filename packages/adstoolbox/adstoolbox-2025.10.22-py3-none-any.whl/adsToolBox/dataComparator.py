import polars as pl
from .timer import timer
from .logger import Logger
from polars.testing import assert_frame_equal

class DataComparator:
    def __init__(self, dictionnary: dict, logger: Logger):
        """
        Initialise un dataComparator avec les informations de connexions aux bases de données
        :param dictionnary: le dictionnaire qui contient les informations du pipeline
            - 'db_source_1': la base de données source 1
            - 'query_source_1': la requête à envoyer à la source 1
            - 'db_source_2': la base de données source 2
            - 'query_source_2': la requête à envoyer à la source 2
            - 'batch_size': la taille des lots pour le traitement en batch
        :param logger: le logger pour gérer la journalisation des évènements du pipeline
        """
        self.logger = logger
        self.__db_source_1 = dictionnary.get('db_source_1')
        self.__query_source_1 = dictionnary.get('query_source_1')
        self.__db_source_2 = dictionnary.get('db_source_2')
        self.__query_source_2 = dictionnary.get('query_source_2')
        self.__batch_size = dictionnary.get('batch_size', 10_000)

    def _fetch_data(self, db, query):
        """
        Exécute la requête donnée sur la base spécifiée et retourne un DataFrame Polars
        :param db: la base sur laquelle envoyer la requête
        :param query: la requête à envoyer
        :return: le résultat de la requête sous forme de DataFrame
        """
        db.connect()
        for batch in db.sqlQuery(query):
            yield pl.DataFrame(batch, orient='row', strict=False, infer_schema_length=self.__batch_size)

    @timer
    def compare(self, check_dtypes: bool = False):
        """
        Compare les résultats des deux requêtes SQL entre les deux bases de données.

        :param check_dtypes: si True, vérifie aussi la stricte égalité des types de colonnes
                             si False (défaut), ne vérifie que les valeurs
        :return: True si les DataFrames sont identiques (selon le niveau de vérification)
        """
        try:
            gen1 = self._fetch_data(self.__db_source_1, self.__query_source_1)
            gen2 = self._fetch_data(self.__db_source_2, self.__query_source_2)
            batch_index = 0
            while True:
                try:
                    df1 = next(gen1)
                except StopIteration:
                    df1 = None
                try:
                    df2 = next(gen2)
                except StopIteration:
                    df2 = None
                if df1 is None and df2 is None:
                    self.logger.info("Les données des deux sources sont identiques.")
                    return True
                if (df1 is None) != (df2 is None):
                    self.logger.error(f"Nombre de lignes différent entre les deux sources.")
                    return False
                batch_index += 1
                try:
                    assert_frame_equal(df1, df2, check_dtypes=check_dtypes)
                except Exception as e:
                    self.logger.error(f"Les données diffèrent dans le batch #{batch_index}: {e}")
                    return False
                self.logger.debug(f"Batch #{batch_index} identique ({len(df1)} lignes).")
        except Exception as e:
            self.logger.error(f"Erreur lors de la comparaison des données : {e}")
            raise