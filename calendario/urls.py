# calendario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Asegúrate que la importación coincida con dónde pusiste el ViewSet
from .views import EventoMedicoViewSet 

# Crear un router y registrar nuestro ViewSet
router = DefaultRouter()
# 'eventos-medicos' será el prefijo de la URL
router.register(r'eventos-medicos', EventoMedicoViewSet, basename='evento-medico')

# Las URLs de la API son determinadas automáticamente por el router.
urlpatterns = [
    # Este archivo SOLO debe manejar las URLs de la API.
    # El prefijo 'api/' ya está en tu 'zanysure/urls.py', 
    # así que aquí solo incluimos el router.
    path('', include(router.urls)),
]