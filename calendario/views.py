from django.shortcuts import render

# calendario/views.py (o api.py)
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import EventoMedico
from .serializers import EventoMedicoSerializer

# ... (Si tienes otras vistas aquí, déjalas) ...

class EventoMedicoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver o editar eventos médicos del usuario autenticado.
    """
    serializer_class = EventoMedicoSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios logueados

    def get_queryset(self):
        """
        Esta vista debe retornar una lista de todos los eventos
        para el usuario autenticado actualmente.
        """
        return EventoMedico.objects.filter(usuario=self.request.user).order_by('fecha_hora_evento')

    def perform_create(self, serializer):
        """
        Asigna el usuario actual al crear un nuevo evento médico.
        """
        serializer.save(usuario=self.request.user)

    # Opcional: Podrías añadir validación extra o lógica en create/update/destroy
    # def create(self, request, *args, **kwargs):
    #     #... lógica antes de crear ...
    #     response = super().create(request, *args, **kwargs)
    #     #... lógica después de crear ...
    #     return response