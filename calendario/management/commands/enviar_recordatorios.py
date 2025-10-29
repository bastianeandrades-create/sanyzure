from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from calendario.models import EventoMedico
from calendario.brevo_utils import enviar_correo_brevo, generar_contenido_y_asunto_desde_plantilla 
import logging

logger = logging.getLogger('calendario') # Usar el logger de la app

class Command(BaseCommand):
    help = 'Busca eventos médicos próximos y envía recordatorios por correo usando Brevo.'

    def handle(self, *args, **options):
        ahora = timezone.now()
        self.stdout.write(f"[{ahora.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando búsqueda de recordatorios...")
        logger.info(f"[{ahora}] Iniciando búsqueda de recordatorios...")

        # Busca eventos que aún no han ocurrido
        eventos_proximos = EventoMedico.objects.filter(fecha_hora_evento__gte=ahora)

        contador_enviados = 0
        contador_errores = 0
        contador_omitidos = 0
        contador_sin_email = 0

        for evento in eventos_proximos:
            logger.debug(f"\n--- Verificando Evento ID {evento.id}: {evento.titulo} ---")
            logger.debug(f"Fecha/Hora Evento (UTC): {evento.fecha_hora_evento}")
            # Convertir a hora local para mayor claridad en el log
            fecha_local_evento = timezone.localtime(evento.fecha_hora_evento)
            logger.debug(f"Fecha/Hora Evento (Local): {fecha_local_evento}")

            destinatario_email = evento.usuario.email
            if not destinatario_email:
                logger.warning(f"Usuario {evento.usuario.username} (ID: {evento.usuario.id}) no tiene email para evento {evento.id}. Saltando.")
                contador_sin_email += 1
                continue

            destinatario_nombre = evento.usuario.get_full_name() or evento.usuario.username

            enviar = False
            ventana_inicio = None # Para lógica anti-duplicados
            tiempo_falta = evento.fecha_hora_evento - ahora # 'ahora' ya está en UTC si USE_TZ=True

            # Log del tiempo restante
            logger.debug(f"Tiempo restante: {tiempo_falta}")
            logger.debug(f"Último recordatorio enviado: {evento.ultimo_recordatorio_enviado}")


            try:
                # Lógica para decidir si enviar
                if evento.tipo_evento in ['cita', 'procedimiento'] and evento.recordatorio_cita_dias:
                    logger.debug(f"Tipo Cita/Procedimiento. Días antes: '{evento.recordatorio_cita_dias}'")
                    dias_antes_lista = sorted([int(d.strip()) for d in evento.recordatorio_cita_dias.split(',') if d.strip().isdigit()], reverse=True)
                    for dias_antes in dias_antes_lista:
                        # --- DEBUG ---
                        limite_superior = timedelta(days=dias_antes)
                        limite_inferior = timedelta(days=dias_antes - 1)
                        logger.debug(f"Probando {dias_antes} días antes: ¿Está {tiempo_falta} entre {limite_inferior} y {limite_superior}?")
                        # --- FIN DEBUG ---
                        if limite_inferior <= tiempo_falta < limite_superior:
                            ventana_inicio = evento.fecha_hora_evento - limite_superior
                            logger.debug(f"Ventana de {dias_antes} días activada. Inicio ventana: {ventana_inicio}")
                            # Comprobar si ya se envió DESPUÉS del inicio de esta ventana
                            if not evento.ultimo_recordatorio_enviado or evento.ultimo_recordatorio_enviado < ventana_inicio:
                                logger.debug("=> DECISIÓN: Enviar (Nuevo o ventana no enviada).")
                                enviar = True
                            else:
                                logger.debug("=> DECISIÓN: No Enviar (Ya enviado para esta ventana).")
                            break # Salir del bucle de días_antes si se encuentra una ventana
                        else:
                            logger.debug("Fuera de esta ventana de días.")

                elif evento.tipo_evento == 'remedio':
                    horas_antes = evento.recordatorio_remedio_horas or 1
                    logger.debug(f"Tipo Remedio. Horas antes: {horas_antes}")
                    # --- DEBUG ---
                    limite_superior = timedelta(hours=horas_antes)
                    limite_inferior = timedelta(hours=horas_antes - 1)
                    logger.debug(f"Probando {horas_antes} horas antes: ¿Está {tiempo_falta} entre {limite_inferior} y {limite_superior}?")
                    # --- FIN DEBUG ---
                    if limite_inferior <= tiempo_falta < limite_superior:
                         ventana_inicio = evento.fecha_hora_evento - limite_superior
                         logger.debug(f"Ventana de {horas_antes} horas activada. Inicio ventana: {ventana_inicio}")
                         if not evento.ultimo_recordatorio_enviado or evento.ultimo_recordatorio_enviado < ventana_inicio:
                             logger.debug("=> DECISIÓN: Enviar (Nuevo o ventana no enviada).")
                             enviar = True
                         else:
                             logger.debug("=> DECISIÓN: No Enviar (Ya enviado para esta ventana).")
                    else:
                         logger.debug("Fuera de esta ventana de horas.")

            except Exception as e:
                 logger.error(f"Error calculando ventana para evento {evento.id}: {e}")
                 contador_errores += 1
                 continue # Saltar este evento

            # --- ESTE BLOQUE 'if/elif/else' ESTÁ AHORA AFUERA DEL 'try' ---
            if enviar:
                # <<< TODO ESTO ESTÁ INDENTADO BAJO EL 'if enviar:' >>>
                logger.info(f"Preparando recordatorio para Evento ID {evento.id} ({evento.tipo_evento}) para {destinatario_email}")
                try:
                    asunto, contenido_html = generar_contenido_y_asunto_desde_plantilla(evento)
                    
                    exito = enviar_correo_brevo(
                        destinatario_email=destinatario_email,
                        destinatario_nombre=destinatario_nombre,
                        asunto=asunto, 
                        contenido_html=contenido_html 
                    )
                    
                    if exito:
                        logger.info(f"Recordatorio ID {evento.id} enviado exitosamente a {destinatario_email}.")
                        # Marcar como enviado AHORA para esta ventana
                        evento.ultimo_recordatorio_enviado = timezone.now()
                        evento.save(update_fields=['ultimo_recordatorio_enviado']) 
                        contador_enviados += 1
                    else:
                        logger.error(f"Fallo al enviar recordatorio ID {evento.id} a {destinatario_email} (función enviar_correo_brevo retornó False).")
                        contador_errores += 1
                        
                except Exception as e:
                    logger.exception(f"Excepción al generar o enviar correo para evento {evento.id}: {e}")
                    contador_errores += 1
            
            elif ventana_inicio and evento.ultimo_recordatorio_enviado and evento.ultimo_recordatorio_enviado >= ventana_inicio:
                 contador_omitidos += 1 # Ya enviado
                 logger.debug(f"Evento {evento.id} omitido (ya enviado recientemente).")
            
            else:
                # No entró en ninguna ventana válida
                logger.debug(f"Evento {evento.id} no cumple criterios de envío en esta ejecución.")
        
        # --- ESTE BLOQUE ESTÁ AHORA AFUERA DEL 'for' ---
        resumen = (f"Proceso finalizado. "
                   f"Enviados: {contador_enviados}, "
                   f"Errores: {contador_errores}, "
                   f"Omitidos (ya enviados): {contador_omitidos}, "
                   f"Sin email: {contador_sin_email}.")
        self.stdout.write(self.style.SUCCESS(resumen))
        logger.info(resumen)
