# calendario/brevo_utils.py
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from django.template.loader import render_to_string 
from django.utils import timezone
import logging

# Usar el logger específico de la app 'calendario' (configurado en settings.py)
logger = logging.getLogger('calendario') 

def enviar_correo_brevo(destinatario_email, destinatario_nombre, asunto, contenido_html, remitente_nombre="Recordatorios Médicos"):
    """Envía un correo electrónico usando la API de Brevo."""
    if not settings.BREVO_API_KEY:
         logger.error("Error: BREVO_API_KEY no está configurada en settings.py o .env.")
         return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    sender = sib_api_v3_sdk.SendSmtpEmailSender(name=remitente_nombre, email=settings.EMAIL_HOST_USER)
    to = [sib_api_v3_sdk.SendSmtpEmailTo(email=destinatario_email, name=destinatario_nombre)]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=to,
        subject=asunto,
        html_content=contenido_html
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Correo enviado a {destinatario_email} via Brevo. Message ID: {api_response.message_id}")
        return True
    except ApiException as e:
        logger.error(f"Error al enviar correo a {destinatario_email} via Brevo API: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al enviar correo a {destinatario_email}: {e}")
        return False

def generar_contenido_y_asunto_desde_plantilla(evento):
    """Genera el asunto y el contenido HTML del correo usando plantillas Django."""
    if evento.tipo_evento == 'cita':
        template_name = 'emails/recordatorio_cita.html'
        asunto_base = f"Recordatorio de Cita Médica: {evento.titulo}"
    elif evento.tipo_evento == 'remedio':
        template_name = 'emails/recordatorio_remedio.html'
        asunto_base = f"Recordatorio: Tomar {evento.titulo}"
    elif evento.tipo_evento == 'procedimiento':
        template_name = 'emails/recordatorio_procedimiento.html'
        asunto_base = f"Recordatorio de Procedimiento Médico: {evento.titulo}"
    else:
        template_name = 'emails/recordatorio_otro.html'
        asunto_base = f"Recordatorio Médico: {evento.titulo}"

    context = {
        'evento': evento,
        'nombre_usuario': evento.usuario.first_name or evento.usuario.username, 
        'asunto': asunto_base,
        'fecha_hora_evento': timezone.localtime(evento.fecha_hora_evento) # Fecha/hora localizada
    }

    contenido_html = render_to_string(template_name, context)
    return asunto_base, contenido_html