# perfil_médico/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilMedico(models.Model):
    # Conectamos cada perfil a un único usuario
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfilmedico")
    
    # --- Datos Personales ---
    edad = models.PositiveIntegerField(blank=True, null=True, help_text="Tu edad actual")
    peso_kg = models.DecimalField(
        max_digits=5, decimal_places=1, blank=True, null=True, 
        help_text="Tu peso actual en kilogramos (ej: 75.5)"
    )
    
    # --- Datos Médicos Clave ---
    condiciones_medicas = models.TextField(
        blank=True, 
        help_text="Ej: Hipertensión, Diabetes tipo 2, Hipotiroidismo"
    )
    alergias = models.TextField(
        blank=True, 
        help_text="Ej: Alergia a la Penicilina, Alergia al Polvo"
    )
    medicamentos_fijos = models.TextField(
        blank=True, 
        help_text="Los medicamentos que tomas permanentemente. Ej: Losartán 50mg (1 al día), Eutirox 100mg (1 en ayunas)"
    )
    contactos_emergencia = models.TextField(
        blank=True, 
        help_text="Ej: Juan Pérez (Hijo) - +56912345678, Dr. Silva (Médico) - +56987654321"
    )

    def __str__(self):
        return f"Perfil Médico de {self.usuario.username}"

# --- ¡MAGIA AUTOMÁTICA! ---
# Esta función se asegura de que cada vez que un Usuario NUEVO se registra,
# se le crea automáticamente un PerfilMedico vacío.
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_de_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilMedico.objects.create(usuario=instance)
    instance.perfilmedico.save()