# menu/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ¡Esta es la línea que estaba causando el error en el otro archivo!
    path('', views.menu_view, name='menu'),
    
    # --- Todas las URLs de tu app de Menú ---
    path('ayuda/', views.ayuda_view, name='ayuda'),
    
    path('tami/', views.tami_view, name='tami'),
    path('tami/about/', views.tami_about_view, name='tami_about'),
    path('tami/solicitudes/', views.solicitudes_view, name='tami_solicitudes'),
    
    path('citas/', views.proximas_citas_view, name='proximas_citas'),
    path('remedios/', views.proximos_remedios_view, name='proximos_remedios'),
    path('procedimientos/', views.procedimientos_view, name='procedimientos'),
    
    path('evento/toggle/<int:evento_id>/', views.toggle_completado_view, name='toggle_completado'),
]