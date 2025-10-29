from django.contrib import admin
from .models import EventoMedico

@admin.register(EventoMedico)
class EventoMedicoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo_evento', 'fecha_hora_evento', 'ultimo_recordatorio_enviado', 'creado_en')
    list_filter = ('tipo_evento', 'usuario', 'fecha_hora_evento')
    search_fields = ('titulo', 'descripcion', 'usuario__username')
    # Hacer el campo de solo lectura en el admin
    readonly_fields = ('ultimo_recordatorio_enviado', 'creado_en', 'actualizado_en') 
    # Organizar campos en el formulario de edición
    fieldsets = (
        (None, {
            'fields': ('usuario', 'tipo_evento', 'titulo', 'descripcion', 'fecha_hora_evento')
        }),
        ('Configuración de Recordatorios', {
            'fields': ('frecuencia_horas', 'recordatorio_cita_dias', 'recordatorio_remedio_horas'),
            'classes': ('collapse',) # Opcional: ocultar por defecto
        }),
         ('Estado Interno', {
            'fields': ('ultimo_recordatorio_enviado', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )