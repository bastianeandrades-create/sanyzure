# calendario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Asegúrate que la importación coincida con dónde pusiste el ViewSet
from .views import EventoMedicoViewSet  # O from .api import EventoMedicoViewSet 

# Crear un router y registrar nuestro ViewSet
router = DefaultRouter()
# 'eventos-medicos' será el prefijo de la URL (ej: /calendario/api/eventos-medicos/)
router.register(r'eventos-medicos', EventoMedicoViewSet, basename='evento-medico')

# Las URLs de la API son determinadas automáticamente por el router.
urlpatterns = [
    # ... (otras urls de tu app 'calendario' si las tienes) ...

    # Incluir las URLs generadas por el router bajo el prefijo 'api/'
    path('api/', include(router.urls)),
]