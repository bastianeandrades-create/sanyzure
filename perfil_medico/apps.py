from django.apps import AppConfig

class PerfilMedicoConfig(AppConfig):
    name = 'perfil_medico'

    def ready(self):
        import perfil_medico.signals


