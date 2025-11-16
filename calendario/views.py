# calendario/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from django.contrib import messages
from .models import EventoMedico
from .forms import EventoForm
from rest_framework import viewsets, permissions
from .serializers import EventoMedicoSerializer
import holidays # ¡NUEVA LIBRERÍA IMPORTADA!

# --- VISTAS DE LA API (Sin cambios) ---

class EventoMedicoViewSet(viewsets.ModelViewSet):
    serializer_class = EventoMedicoSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return EventoMedico.objects.filter(usuario=self.request.user).order_by('fecha_hora_evento')
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# --- VISTAS DE LA PÁGINA WEB ---

@login_required
def calendario_view(request):
    """
    Vista principal del calendario.
    (AHORA CON CÓDIGOS DE COLOR PARA LOS DÍAS)
    """
    
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.usuario = request.user
            evento.save()
            messages.success(request, f'¡Evento "{evento.titulo}" añadido con éxito!')
            return redirect('calendario')
        else:
            messages.error(request, 'Error al añadir el evento. Por favor, revise los campos.')

    # --- Lógica GET (Construir la línea de tiempo de SEMANAS) ---
    
    # 1. Obtener eventos
    eventos_del_usuario = EventoMedico.objects.filter(usuario=request.user)
    eventos_por_fecha = {}
    for evento in eventos_del_usuario:
        fecha_evento = evento.fecha_hora_evento.date()
        if fecha_evento not in eventos_por_fecha:
            eventos_por_fecha[fecha_evento] = []
        eventos_por_fecha[fecha_evento].append(evento)
    
    # --- ¡NUEVO! Inicializar el calendario de feriados ---
    # Usamos 'CL' para Chile. ¡Puedes cambiar esto al código de tu país!
    try:
        feriados_chile = holidays.CL() 
    except ImportError:
        feriados_chile = {} # Fallback si la librería falla
        
    # 2. Determinar el rango de fechas
    today = timezone.now().date()
    primera_fecha_interes = today - timedelta(days=30)
    ultima_fecha_interes = today + timedelta(days=90)
    
    if eventos_del_usuario.exists():
        primera_fecha_evento = eventos_del_usuario.earliest('fecha_hora_evento').fecha_hora_evento.date()
        ultima_fecha_evento = eventos_del_usuario.latest('fecha_hora_evento').fecha_hora_evento.date()
        primera_fecha_interes = min(primera_fecha_interes, primera_fecha_evento - timedelta(days=7))
        ultima_fecha_interes = max(ultima_fecha_interes, ultima_fecha_evento + timedelta(days=30))

    start_date = primera_fecha_interes - timedelta(days=primera_fecha_interes.weekday())
    end_date = ultima_fecha_interes + timedelta(days=(6 - ultima_fecha_interes.weekday()))

    # 5. Construir la lista de días COMPLETA (con los nuevos flags)
    all_days_data = []
    current_date = start_date
    while current_date <= end_date:
        is_placeholder = current_date < primera_fecha_interes or current_date > ultima_fecha_interes
        
        all_days_data.append({
            'date_obj': current_date,
            'is_today': current_date == today,
            'is_placeholder': is_placeholder,
            'events': sorted(eventos_por_fecha.get(current_date, []), key=lambda e: e.fecha_hora_evento.time()),
            'date_iso': current_date.isoformat(),
            'month_year': current_date.strftime("%B %Y").capitalize(),
            'is_first_of_month': current_date.day == 1,
            
            # --- ¡NUEVOS FLAGS DE COLOR! ---
            'day_of_week': current_date.weekday(), # 0=Lunes, 5=Sábado, 6=Domingo
            'is_past': current_date < today,
            'is_holiday': current_date in feriados_chile and not is_placeholder,
            # --- FIN DE NUEVOS FLAGS ---
        })
        current_date += timedelta(days=1)

    # 6. Agrupar la lista de días en semanas
    weeks_data = []
    for i in range(0, len(all_days_data), 7):
        semana = all_days_data[i:i + 7]
        
        first_day_header = semana[0]['month_year']
        last_day_header = semana[6]['month_year']
        
        header_text = first_day_header
        if first_day_header != last_day_header:
            header_text = f"{first_day_header} / {last_day_header}"

        weeks_data.append({
            'dias': semana,
            'month_year_header': header_text, 
            'week_id': f"week-{semana[0]['date_iso']}"
        })

    # 7. Preparar el formulario vacío
    form = EventoForm()

    context = {
        'weeks_data': weeks_data,
        'today_week_id': f"week-{ (today - timedelta(days=today.weekday())).isoformat() }",
        'form': form,
    }
    return render(request, 'calendario/calendario.html', context)


@login_required
def editar_evento_view(request, evento_id):
    evento = get_object_or_404(EventoMedico, id=evento_id, usuario=request.user)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Evento "{evento.titulo}" actualizado!')
            return redirect('calendario')
        else:
            messages.error(request, 'Error al actualizar. Revise los campos.')
    else:
        form = EventoForm(instance=evento)

    context = {
        'form': form,
        'evento': evento,
    }
    return render(request, 'calendario/editar_evento.html', context)


@login_required
def borrar_evento_view(request, evento_id):
    evento = get_object_or_404(EventoMedico, id=evento_id, usuario=request.user)
    
    if request.method == 'POST':
        titulo_evento = evento.titulo
        evento.delete()
        messages.success(request, f'Evento "{titulo_evento}" borrado con éxito.')
    
    return redirect('calendario')