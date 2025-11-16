# perfil_médico/forms.py
from django import forms
from .models import PerfilMedico

class PerfilMedicoForm(forms.ModelForm):
    class Meta:
        model = PerfilMedico
        # Incluimos los campos que el usuario puede editar
        fields = [
            'edad', 
            'peso_kg', 
            'condiciones_medicas', 
            'alergias', 
            'medicamentos_fijos', 
            'contactos_emergencia'
        ]
        widgets = {
            'edad': forms.NumberInput(attrs={'class': 'form-control-accessible', 'placeholder': 'Ej: 72'}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control-accessible', 'placeholder': 'Ej: 80.5'}),
            'condiciones_medicas': forms.Textarea(attrs={'class': 'form-control-accessible', 'rows': 4}),
            'alergias': forms.Textarea(attrs={'class': 'form-control-accessible', 'rows': 4}),
            'medicamentos_fijos': forms.Textarea(attrs={'class': 'form-control-accessible', 'rows': 4}),
            'contactos_emergencia': forms.Textarea(attrs={'class': 'form-control-accessible', 'rows': 4}),
        }
        labels = {
            'edad': '¿Cuál es tu edad?',
            'peso_kg': '¿Cuál es tu peso actual (en Kg)?',
            'condiciones_medicas': 'Condiciones Médicas (Ej: Hipertensión)',
            'alergias': 'Alergias Conocidas (Ej: Penicilina)',
            'medicamentos_fijos': 'Medicamentos Fijos (Ej: Losartán 1 al día)',
            'contactos_emergencia': 'Contactos de Emergencia (Nombre y Teléfono)',
        }