# login/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL: /login/
    path('', views.user_login, name='login'), 
    
    # URL: /login/logout/
    path('logout/', views.user_logout, name='logout'), 
    
    # NUEVA URL: /login/registro/
    path('registro/', views.user_register, name='registro'),
]