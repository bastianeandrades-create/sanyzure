from django.urls import path
from . import views

app_name = 'perfil'

urlpatterns = [
    path('', views.profile_view, name='profile_view'),
    path('editar/', views.edit_profile, name='edit_profile'),
    path('medicacion/add/', views.add_medication, name='add_medication'),
    path('medicacion/<int:med_id>/edit/', views.edit_medication, name='edit_medication'),
    path('medicacion/<int:med_id>/delete/', views.delete_medication, name='delete_medication'),
    path('examen/add/', views.add_labtest, name='add_labtest'),
]
