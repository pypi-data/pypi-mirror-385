import os
import dotenv
import inspect

class env:
    def __init__(self, logger, file=None):
        """
        Recherche et charge un fichier .env.
        - Si 'file' est fourni : charge ce fichier s'il existe.
        - Sinon : cherche automatiquement le .env le plus proche en remontant
          depuis le dossier du script exécuté.
        """
        self.logger = logger

        # --- Cas 1 : fichier spécifié explicitement
        if file and os.path.isfile(file):
            dotenv_file = os.path.abspath(file)
            dotenv.load_dotenv(dotenv_file, override=True)
            self.logger.debug(f"Fichier .env spécifié trouvé et chargé : {dotenv_file}")

        # --- Cas 2 : recherche automatique
        else:
            caller_file = inspect.stack()[1].filename
            caller_dir = os.path.dirname(os.path.abspath(caller_file))
            dotenv_file = self._find_env_upwards(caller_dir)
            if dotenv_file:
                dotenv.load_dotenv(dotenv_file, override=True)
                self.logger.debug(f"Fichier .env trouvé automatiquement : {dotenv_file}")
            else:
                self.logger.warning("Aucun fichier .env trouvé en remontant depuis le script.")
                self.logger.warning("Veuillez créer un fichier .env à la racine du projet ou en spécifier un manuellement.")

        # --- Synchronisation des variables dans l'objet
        for cle, valeur in os.environ.items():
            setattr(self, cle, valeur)

    def _find_env_upwards(self, start_path):
        """Recherche récursivement un fichier .env en remontant les dossiers"""
        current_dir = start_path
        while True:
            self.logger.debug(f"Recherche d'un fichier .env dans : {current_dir}")
            candidate = os.path.join(current_dir, '.env')
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir
        return None