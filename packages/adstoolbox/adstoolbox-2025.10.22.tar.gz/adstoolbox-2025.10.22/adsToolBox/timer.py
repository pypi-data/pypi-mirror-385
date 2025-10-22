import os
import time
import timeit
from .global_config import get_timer

def timer(func):
    """
    Décorateur pour mesurer le temps d'exécution d'une fonction et enregistrer ce temps dans un logger si activé.
    :param func: La fonction à décorer pour mesurer et enregistrer son temps d'exécution.
    :raises ValueError: Si aucun logger n'est défini dans les arguments de la fonction appelée.
    :return: La fonction décorée qui mesure le temps d'exécution.
    """
    def wrapper(*args, **kwargs):
        if get_timer():
            logger = kwargs.get('logger', None)
            if logger is None and args and hasattr(args[0], 'logger'):
                logger = args[0].logger
            if logger is None: raise ValueError("Pas de logger défini.")
            start_time = timeit.default_timer()
            result = func(*args, **kwargs)
            elapsed_time = timeit.default_timer() - start_time
            if logger is not None:
                logger.info(f"Temps d'exécution de {func.__name__}: {elapsed_time:.4f} secondes.")
            return result
        else:
            return func(*args, **kwargs)
    return wrapper

def set_timezone(tz='Europe/Paris'):
    """Définit le fuseau horaire global du processus"""
    os.environ['TZ'] = tz
    if hasattr(time, 'tzset'):
        time.tzset()
        print(f"[INFO] Fuseau horaire défini globalement sur {tz} (via time.tzset)")
    else:
        from zoneinfo import ZoneInfo
        global _GLOBAL_TZ
        _GLOBAL_TZ = ZoneInfo(tz)
        print(f"[WARNING] Fuseau horaire simulé sur {tz} (Windows n’a pas tzset())")
        print(f"Appeler ads.now() pour avoir l'heure simulée sur {tz}")

def now():
    """Renvoie l'heure actuelle dans le fuseau global défini"""
    from datetime import datetime
    if '_GLOBAL_TZ' in globals():
        return datetime.now(_GLOBAL_TZ)
    return datetime.now()