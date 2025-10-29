# menu/urls.py
from django.urls import path
from . import views # Importa el archivo views.py de la app menu

urlpatterns = [
    # Cuando alguien vaya a la URL raíz de 'menu/' (definida en zanysure/urls.py),
    # se ejecutará la función menu_view de menu/views.py
    path('', views.menu_view, name='menu'), 
    
    # Si tienes más URLs para la app 'menu', añádelas aquí.
]