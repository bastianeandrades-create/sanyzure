# calendario/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import EventoMedico

class EventoMedicoSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    # Mostrar el tipo de evento de forma legible
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True) 

    class Meta:
        model = EventoMedico
        # Campos a incluir en la API
        fields = [
            'id', 
            'usuario', 
            'usuario_username',
            'tipo_evento', 
            'tipo_evento_display',
            'titulo', 
            'descripcion', 
            'fecha_hora_evento',
            'frecuencia_horas', 
            'recordatorio_cita_dias', 
            'recordatorio_remedio_horas',
            # 'ultimo_recordatorio_enviado', # Podrías exponerlo si es útil (read_only)
            'creado_en',
            'actualizado_en'
        ]
        # El usuario se asigna automáticamente, no se debe enviar en el POST/PUT
        read_only_fields = ['usuario', 'creado_en', 'actualizado_en'] 

    # Validación para asegurar que la fecha no sea en el pasado al crear/actualizar
    def validate_fecha_hora_evento(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("La fecha y hora del evento no puede ser en el pasado.")
        return value