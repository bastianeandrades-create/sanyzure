# zanysure/urls.py

from django.contrib import admin
from django.urls import path, include
from login import views as login_views
from calendario import views as calendario_views
from perfil_médico import views as perfil_views # ¡Importamos las vistas de perfil!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('api/', include('calendario.urls')), 
    path('menu/', include('menu.urls')),
    
    # La URL raíz
    path('', login_views.index_redirect_view, name='index_redirect'),
    
    # Tus URLs de login personalizadas
    path('login/', include('login.urls')), 
    
    # --- RUTAS DEL CALENDARIO ---
    path('calendario/', calendario_views.calendario_view, name='calendario'),
    path('calendario/editar/<int:evento_id>/', 
         calendario_views.editar_evento_view, 
         name='editar_evento'),
    path('calendario/borrar/<int:evento_id>/', 
         calendario_views.borrar_evento_view, 
         name='borrar_evento'),
    
    # --- ¡RUTAS DEL PERFIL MÉDICO ACTUALIZADAS! ---
    
    # 1. El "Hub" del perfil
    path('perfil/', perfil_views.perfil_view, name='perfil'),
    
    # 2. ¡NUEVA! La página para editar el formulario
    path('perfil/editar/', perfil_views.perfil_editar_view, name='perfil_editar'),
    
    # 3. La URL para exportar (ahora acepta ?tipo=...)
    path('perfil/exportar_pdf/', 
         perfil_views.exportar_perfil_pdf, 
         name='exportar_perfil_pdf'),
]