# calendario/apps.py

from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class CalendarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendario'

    def ready(self):
        """
        Este método se llama automáticamente cuando la app 'calendario' está lista.
        """
        # Verificamos que no estemos en un subproceso (como el 'reloader' de Django)
        # para evitar que el programador se inicie dos veces.
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            logger.info("Iniciando el programador de tareas (APScheduler)...")
            from . import scheduler
            scheduler.start()
        else:
            logger.info("APScheduler: Evitando doble inicio (probablemente en 'reloader').")