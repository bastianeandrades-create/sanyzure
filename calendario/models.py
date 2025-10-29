# calendario/models.py
from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone

class EventoMedico(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('cita', 'Cita Médica'),
        ('remedio', 'Toma de Remedio'),
        ('procedimiento', 'Procedimiento Médico'),
        ('otro', 'Otro'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_medicos') 
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    titulo = models.CharField(max_length=200, help_text="Ej: Cita con Dr. López, Tomar Paracetamol 500mg")
    descripcion = models.TextField(blank=True, null=True, help_text="Detalles adicionales, indicaciones, etc.")
    fecha_hora_evento = models.DateTimeField(help_text="Fecha y hora del evento médico.")
    frecuencia_horas = models.PositiveIntegerField(blank=True, null=True, help_text="Para remedios, indicar cada cuántas horas tomar (ej: 8)")
    recordatorio_cita_dias = models.CharField(max_length=50, blank=True, help_text="Días antes para recordar citas/procs (ej: '7,3,1')")
    recordatorio_remedio_horas = models.PositiveIntegerField(default=1, help_text="Horas antes para recordar toma de remedio")

    # Campo para evitar duplicados (versión simple)
    ultimo_recordatorio_enviado = models.DateTimeField(blank=True, null=True, editable=False)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        fecha_local = timezone.localtime(self.fecha_hora_evento)
        return f"{self.get_tipo_evento_display()}: {self.titulo} ({self.usuario.username}) - {fecha_local.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        ordering = ['fecha_hora_evento'] 
        verbose_name = "Evento Médico" # Nombre legible en admin
        verbose_name_plural = "Eventos Médicos"