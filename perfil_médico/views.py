# perfil_médico/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PerfilMedico
from .forms import PerfilMedicoForm
from calendario.models import EventoMedico
from django.utils import timezone
from datetime import date

# --- ¡NUEVAS IMPORTACIONES PARA EL PDF PROFESIONAL! ---
from django.http import HttpResponse
from django.conf import settings
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors # ¡Para los colores!
from reportlab.platypus import Paragraph # Para texto con formato
from reportlab.lib.styles import ParagraphStyle

# --- Colores de la App (en formato ReportLab) ---
COLOR_PRIMARIO = colors.HexColor("#66D9D9")
COLOR_SECUNDARIO = colors.HexColor("#004a99")
COLOR_TEXTO = colors.HexColor("#1d1d1f")
COLOR_CITA = colors.HexColor("#007bff")
COLOR_REMEDIO = colors.HexColor("#28a745")
COLOR_PROCEDIMIENTO = colors.HexColor("#ffc107")
COLOR_GRIS = colors.HexColor("#888888")

# --- Estilos de Párrafo (para la fuente 'Lato' o 'Helvetica') ---
styles = getSampleStyleSheet()
style_body = ParagraphStyle('Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=14, textColor=COLOR_TEXTO)
style_body_bold = ParagraphStyle('BodyBold', parent=style_body, fontName='Helvetica-Bold')

# CORRECCIÓN DE SCOPE: Recibe page_height como argumento
def draw_wrapped_paragraph(c, text, x, y, max_width, style, page_height, indent=0):
    """Dibuja un Párrafo de ReportLab (permite <b> <i> etc.)"""
    if not text:
        text = "<i>No informado.</i>"
    
    # Reemplazamos saltos de línea manuales por <br/>
    text = text.replace('\n', '<br/>')
    
    p = Paragraph(text, style)
    # CORRECCIÓN: Usa page_height para la envoltura de texto
    p.wrapOn(c, max_width - indent, page_height) 
    p_height = p.height
    p.drawOn(c, x + indent, y - p_height) # Dibujar
    return y - p_height - (0.1 * inch) # Devuelve la nueva posición 'y'

def check_page_break(c, y, margin, page_height):
    """Añade una nueva página si 'y' está muy abajo"""
    if y < margin + (1 * inch):
        c.showPage() # Nueva página
        c.setFont('Helvetica', 10)
        y = page_height - margin - (0.5 * inch) # Reiniciar 'y'
        c.drawString(margin, y, "--- (Continuación) ---")
        y -= (0.5 * inch)
    return y


# --- VISTA 1: El "Hub" o Centro de Control del Perfil (Sin cambios) ---
@login_required
def perfil_view(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'perfil_médico/perfil.html', context)


# --- VISTA 2: La Página de "Editar" el Formulario (Sin cambios) ---
@login_required
def perfil_editar_view(request):
    perfil, created = PerfilMedico.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = PerfilMedicoForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil médico ha sido actualizado con éxito!')
            return redirect('perfil')
    else:
        form = PerfilMedicoForm(instance=perfil)
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
        'form': form
    }
    return render(request, 'perfil_médico/perfil_editar.html', context)


# --- VISTA 3: El Exportador de PDF (¡RECONSTRUIDO CON COLORES!) ---
@login_required
def exportar_perfil_pdf(request):
    """
    Genera un PDF profesional con el resumen médico y el historial de eventos.
    """
    # 1. Preparar el documento PDF
    tipo_export = request.GET.get('tipo', 'todo').strip().lower() # Lectura robusta
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Definición de variables de página
    width, height = letter
    page_height = height 
    
    margin = 0.75 * inch
    max_width = width - (2 * margin)
    y = height - margin

    # --- 2. Añadir el Logo y Título ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width - margin - (2 * inch), height - margin - (0.7 * inch), 
                    width=2*inch, height=0.7*inch, 
                    preserveAspectRatio=True, mask='auto', anchor='ne')

    titulo_pdf = "Resumen Médico Completo"
    if tipo_export == 'cita':
        titulo_pdf = "Historial de Citas Médicas"
    elif tipo_export == 'remedio':
        titulo_pdf = "Historial de Remedios"
    elif tipo_export == 'procedimiento':
        titulo_pdf = "Historial de Procedimientos"
    
    c.setFont('Helvetica-Bold', 24)
    c.setFillColor(COLOR_SECUNDARIO)
    c.drawString(margin, height - margin - (0.5 * inch), titulo_pdf)
    y = height - margin - (1 * inch)
    
    c.setFont('Helvetica', 12)
    c.setFillColor(COLOR_TEXTO)
    c.drawString(margin, y, f"Paciente: {request.user.get_full_name() or request.user.username}")
    y -= 20
    c.drawString(margin, y, f"Fecha del Reporte: {date.today().strftime('%d/%m/%Y')}")
    y -= 40
    
    c.setStrokeColor(COLOR_PRIMARIO) # Línea turquesa
    c.setLineWidth(2)
    c.line(margin, y, width - margin, y + 5)
    y -= 30

    # --- 3. Escribir el Perfil Médico (SOLO si es 'todo') ---
    if tipo_export == 'todo':
        try:
            perfil = request.user.perfilmedico
        except PerfilMedico.DoesNotExist:
            perfil = None

        if perfil:
            c.setFont('Helvetica-Bold', 16)
            c.setFillColor(COLOR_SECUNDARIO)
            c.drawString(margin, y, "Datos del Paciente")
            y -= 30
            
            c.setFont('Helvetica-Bold', 12)
            c.setFillColor(COLOR_TEXTO)
            c.drawString(margin, y, f"Edad: {perfil.edad or 'No informado.'} años")
            c.drawString(margin + (3 * inch), y, f"Peso: {perfil.peso_kg or 'No informado.'} kg")
            y -= 40
            
            c.setFont('Helvetica-Bold', 14)
            c.setFillColor(COLOR_SECUNDARIO)
            c.drawString(margin, y, "Condiciones Médicas:")
            # Se pasa page_height
            y = draw_wrapped_paragraph(c, perfil.condiciones_medicas, margin, y, max_width, style_body, page_height, indent=0.2*inch)

            y = check_page_break(c, y, margin, page_height)
            c.setFont('Helvetica-Bold', 14)
            c.setFillColor(COLOR_SECUNDARIO)
            c.drawString(margin, y, "Alergias:")
            # Se pasa page_height
            y = draw_wrapped_paragraph(c, perfil.alergias, margin, y, max_width, style_body, page_height, indent=0.2*inch)

            y = check_page_break(c, y, margin, page_height)
            c.setFont('Helvetica-Bold', 14)
            c.setFillColor(COLOR_SECUNDARIO)
            c.drawString(margin, y, "Medicamentos Fijos:")
            # Se pasa page_height
            y = draw_wrapped_paragraph(c, perfil.medicamentos_fijos, margin, y, max_width, style_body, page_height, indent=0.2*inch)
            
            y = check_page_break(c, y, margin, page_height)
            c.setFont('Helvetica-Bold', 14)
            c.setFillColor(COLOR_SECUNDARIO)
            c.drawString(margin, y, "Contactos de Emergencia:")
            # Se pasa page_height
            y = draw_wrapped_paragraph(c, perfil.contactos_emergencia, margin, y, max_width, style_body, page_height, indent=0.2*inch)
            y -= 40
    
    # --- 5. Escribir el Historial de Eventos Pasados ---
    c.setFont('Helvetica-Bold', 18)
    c.setFillColor(COLOR_SECUNDARIO)
    c.drawString(margin, y, "Historial de Eventos Pasados")
    y -= 40
    
    filtro_eventos = {'usuario': request.user, 'fecha_hora_evento__lt': timezone.now()}
    
    if tipo_export in ['cita', 'remedio', 'procedimiento']:
        filtro_eventos['tipo_evento'] = tipo_export
    else:
        filtro_eventos['tipo_evento__in'] = ['cita', 'remedio', 'procedimiento']
        
    eventos_pasados = EventoMedico.objects.filter(**filtro_eventos).order_by('-fecha_hora_evento')
    
    if not eventos_pasados.exists():
        c.setFont('Helvetica', 12)
        c.setFillColor(COLOR_GRIS)
        c.drawString(margin, y, "No hay eventos pasados registrados para esta categoría.")
    else:
        for evento in eventos_pasados:
            y = check_page_break(c, y, margin, page_height)
            
            # Definir el color basado en el tipo
            color_evento = COLOR_TEXTO
            if evento.tipo_evento == 'cita': color_evento = COLOR_CITA
            elif evento.tipo_evento == 'remedio': color_evento = COLOR_REMEDIO
            elif evento.tipo_evento == 'procedimiento': color_evento = COLOR_PROCEDIMIENTO

            # Dibujar la barra de color
            c.setFillColor(color_evento)
            c.rect(margin, y - (0.2 * inch), 0.1 * inch, 0.25 * inch, fill=1, stroke=0)
            
            indent_evento = 0.2 * inch
            
            # 1. Título (Negrita y con color)
            c.setFont('Helvetica-Bold', 12)
            c.setFillColor(color_evento)
            fecha_hora = evento.fecha_hora_evento.strftime('%d/%m/%Y a las %H:%M hs')
            # Se pasa page_height
            y = draw_wrapped_paragraph(c, f"{fecha_hora} - {evento.titulo}", margin, y, max_width, style_body_bold, page_height, indent=indent_evento)
            
            # 2. Tipo de Evento
            c.setFont('Helvetica', 10)
            c.setFillColor(COLOR_TEXTO)
            # Se pasa page_height
            y = draw_wrapped_paragraph(c, f"<b>Tipo:</b> {evento.get_tipo_evento_display()}", margin, y, max_width, style_body, page_height, indent=indent_evento)
            
            # 3. Descripción (si existe)
            if evento.descripcion:
                # Se pasa page_height
                y = draw_wrapped_paragraph(c, f"<b>Descripción:</b> {evento.descripcion}", margin, y, max_width, style_body, page_height, indent=indent_evento)
            
            # 4. Estado (si no es una cita)
            if evento.tipo_evento != 'cita':
                estado = "<b>Estado:</b> <font color='green'>Completado</font>" if evento.completado else "<b>Estado:</b> <font color='red'>Pendiente</font>"
                # Se pasa page_height
                y = draw_wrapped_paragraph(c, estado, margin, y, max_width, style_body, page_height, indent=indent_evento)
            
            y -= (0.25 * inch)

    # --- 6. Finalizar el PDF ---
    c.showPage()
    c.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resumen_{tipo_export}_{request.user.username}.pdf"'
    return response