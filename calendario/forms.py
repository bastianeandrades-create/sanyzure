# calendario/forms.py

from django import forms
from .models import EventoMedico

class EventoForm(forms.ModelForm):
    """
    Formulario para crear y editar eventos médicos.
    """
    
    # Hacemos que la fecha y hora usen el widget moderno de HTML
    fecha_hora_evento = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control-accessible'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = EventoMedico
        # Incluimos todos los campos que el usuario debe llenar
        fields = [
            'tipo_evento', 
            'titulo', 
            'descripcion', 
            'fecha_hora_evento',
            'frecuencia_horas',
            'recordatorio_cita_dias',
            'recordatorio_remedio_horas'
        ]
        # Excluimos 'usuario' porque se asignará automáticamente
        exclude = ('usuario',)

    def __init__(self, *args, **kwargs):
        # Este __init__ es para añadir las clases de CSS a todos los campos
        super().__init__(*args, **kwargs)
        
        # Asignamos la clase CSS a todos los campos para que se vean grandes
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({'class': 'form-control-accessible'})
            
            # Personalizar placeholders (textos de ayuda)
            if field_name == 'titulo':
                field.widget.attrs['placeholder'] = 'Ej: Cita con Dr. López'
            if field_name == 'descripcion':
                field.widget.attrs['placeholder'] = 'Ej: Llevar exámenes de sangre'
            if field_name == 'frecuencia_horas':
                field.widget.attrs['placeholder'] = 'Ej: 8 (para remedios cada 8 horas)'
            if field_name == 'recordatorio_cita_dias':
                field.widget.attrs['placeholder'] = 'Ej: 7,3,1 (días antes para recordar)'