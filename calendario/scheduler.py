# calendario/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command
from django.conf import settings
import logging

# Configura un logger para ver qué hace el programador
logger = logging.getLogger(__name__)

def enviar_recordatorios_job():
    """
    Esta es la función que se ejecutará en el intervalo programado.
    Llama a tu comando de gestión 'enviar_recordatorios'.
    """
    try:
        # Usamos el logger de la app 'calendario' que ya tienes configurado
        job_logger = logging.getLogger('calendario') 
        job_logger.info("--- [APScheduler] Iniciando ejecución automática de 'enviar_recordatorios' ---")
        
        call_command('enviar_recordatorios')
        
        job_logger.info("--- [APScheduler] Finalizada ejecución automática de 'enviar_recordatorios' ---")
    
    except Exception as e:
        logger.error(f"[APScheduler] Error al ejecutar 'enviar_recordatorios': {e}", exc_info=True)

def start():
    """
    Inicia el programador de tareas (scheduler).
    """
    # Configura el programador para que use la zona horaria de tu settings.py
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    
    # Añade el "almacén de tareas" de Django.
    # Esto permite que las tareas programadas se guarden en tu base de datos (db.sqlite3)
    # y persistan incluso si reinicias el servidor.
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Programamos la tarea 'enviar_recordatorios_job'
    scheduler.add_job(
        enviar_recordatorios_job,
        trigger='interval',         # Se ejecutará en intervalos
        minutes=30,                 # <--- ¡IMPORTANTE! Ejecutar cada 30 minutos
                                    # Puedes cambiar esto a 15, 60, etc.
        id='enviar_recordatorios_job',
        jobstore='default',
        replace_existing=True       # Reemplaza la tarea si ya existe una con el mismo id
    )
    
    logger.info("Tarea 'enviar_recordatorios_job' programada para ejecutarse cada 30 minutos.")

    try:
        if scheduler.state == 0: # 0 = STATE_STOPPED
            scheduler.start()
            logger.info("Programador de tareas (APScheduler) iniciado.")
        else:
            logger.info("Programador de tareas (APScheduler) ya estaba corriendo.")
    except KeyboardInterrupt:
        logger.info("Deteniendo el programador...")
        scheduler.shutdown()
        logger.info("Programador detenido.")
    except Exception as e:
        logger.error(f"No se pudo iniciar el programador: {e}", exc_info=True)