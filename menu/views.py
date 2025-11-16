# menu/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from calendario.models import EventoMedico 
from django.utils import timezone
from datetime import timedelta, date

@login_required
def menu_view(request):
    """
    Muestra el menú principal y los eventos de los próximos 7 días.
    """
    ahora = timezone.now()
    siete_dias_despues = ahora + timedelta(days=7)

    eventos_proximos = EventoMedico.objects.filter(
        usuario=request.user,
        fecha_hora_evento__gte=ahora,
        fecha_hora_evento__lte=siete_dias_despues
    ).order_by('fecha_hora_evento')

    context = {
        'eventos_proximos': eventos_proximos,
        'nombre_usuario': request.user.first_name or request.user.username
    }
    return render(request, 'menu/menu.html', context)


@login_required
def ayuda_view(request):
    """
    Muestra la página de "Preguntas Frecuentes y Tutoriales".
    """
    return render(request, 'menu/ayuda.html')


@login_required
def tami_view(request):
    """
    Muestra la página de la asistente Tami.
    """
    context = {
        'nombre_usuario': request.user.first_name or request.user.username
    }
    return render(request, 'menu/tami.html', context)


@login_required
def tami_about_view(request):
    """
    Muestra la página con la historia y presentación de Tami.
    """
    context = {
        'nombre_usuario': request.user.first_name or request.user.username
    }
    return render(request, 'menu/tami_about.html', context)


# --- VISTA ACTUALIZADA ---
@login_required
def solicitudes_view(request):
    """
    Muestra un historial de las solicitudes (eventos creados).
    """
    solicitudes_recientes = EventoMedico.objects.filter(
        usuario=request.user
    ).order_by('-creado_en') # Ordenados por fecha de CREACIÓN

    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
        'eventos_proximos': solicitudes_recientes, # Lo pasamos como 'eventos_proximos'
        'eventos_pasados': None, # No hay pasados en esta vista
        'titulo_pagina': "Historial de Solicitudes",
        'subtitulo_pagina': "Todos los eventos que has creado, del más nuevo al más viejo."
    }
    return render(request, 'menu/lista_eventos.html', context)


# --- VISTA ACTUALIZADA ---
@login_required
def proximas_citas_view(request):
    """
    Muestra la lista de PRÓXIMAS CITAS MÉDICAS y las pasadas.
    """
    ahora = timezone.now()
    
    # 1. Citas futuras
    citas_proximas = EventoMedico.objects.filter(
        usuario=request.user,
        tipo_evento='cita',
        fecha_hora_evento__gte=ahora
    ).order_by('fecha_hora_evento')
    
    # 2. Citas pasadas (en orden descendente)
    citas_pasadas = EventoMedico.objects.filter(
        usuario=request.user,
        tipo_evento='cita',
        fecha_hora_evento__lt=ahora
    ).order_by('-fecha_hora_evento')

    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
        'eventos_proximos': citas_proximas,
        'eventos_pasados': citas_pasadas, # ¡NUEVO!
        'titulo_pagina': "Mis Próximas Citas"
    }
    return render(request, 'menu/lista_eventos.html', context)


# --- VISTA ACTUALIZADA ---
@login_required
def proximos_remedios_view(request):
    """
    Muestra la lista de PRÓXIMOS REMEDIOS y los pasados.
    """
    ahora = timezone.now()
    
    # 1. Remedios futuros
    remedios_proximos = EventoMedico.objects.filter(
        usuario=request.user,
        tipo_evento='remedio',
        fecha_hora_evento__gte=ahora
    ).order_by('fecha_hora_evento')

    # 2. Remedios pasados
    remedios_pasados = EventoMedico.objects.filter(
        usuario=request.user,
        tipo_evento='remedio',
        fecha_hora_evento__lt=ahora
    ).order_by('-fecha_hora_evento')

    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
        'eventos_proximos': remedios_proximos,
        'eventos_pasados': remedios_pasados, # ¡NUEVO!
        'titulo_pagina': "Mis Próximos Remedios"
    }
    return render(request, 'menu/lista_eventos.html', context)


# --- VISTAS SIN CAMBIOS (las dejamos como están) ---

@login_required
def procedimientos_view(request):
    """
    Muestra las tareas de HOY (remedios, procedimientos) para marcar como completadas.
    """
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    tareas_hoy = EventoMedico.objects.filter(
        usuario=request.user,
        tipo_evento__in=['remedio', 'procedimiento'],
        fecha_hora_evento__range=(today_start, today_end)
    ).order_by('completado', 'fecha_hora_evento')

    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
        'tareas': tareas_hoy,
        'fecha_hoy': date.today()
    }
    return render(request, 'menu/procedimientos.html', context)

@login_required
def toggle_completado_view(request, evento_id):
    """
    Marca un evento (remedio/proc) como completado o no completado.
    """
    if request.method == 'POST':
        evento = get_object_or_404(EventoMedico, id=evento_id, usuario=request.user)
        
        evento.completado = not evento.completado
        evento.save()
    
    return redirect('procedimientos')