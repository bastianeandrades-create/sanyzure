# login/urls.py
from django.urls import path
from . import views # Importa el archivo views.py de la misma carpeta

urlpatterns = [
    # Cuando alguien vaya a la URL raíz de 'login/' (definida en zanysure/urls.py),
    # se ejecutará la función user_login de login/views.py
    path('', views.user_login, name='login'), 
    
    # Si tienes otras URLs para esta app (ej: registro, logout), añádelas aquí.
    # path('registro/', views.registro_view, name='registro'), 
    # path('logout/', views.logout_view, name='logout'), 
]