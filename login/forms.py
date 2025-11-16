# login/forms.py

from django import forms
from django.contrib.auth.models import User

# --- 1. TU LOGIN FORM (CORREGIDO CON ':') ---
class LoginForm(forms.Form): # <--- AQUÍ ESTABA EL ERROR, FALTABA EL ':'
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# --- 2. EL FORMULARIO DE REGISTRO QUE AÑADIMOS ---
class UserRegistrationForm(forms.ModelForm):
    # Campo de Email, lo hacemos requerido
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    # Campo de Contraseña
    password = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    # Campo para confirmar Contraseña
    password2 = forms.CharField(
        label='Confirmar contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        # Comprueba que las dos contraseñas coincidan
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

    def clean_email(self):
        # Comprueba que el email no esté ya en uso
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email