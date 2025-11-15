from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MedicalProfile, Medication, LabTest
from .forms import MedicalProfileForm, MedicationForm, LabTestForm

# hook: reemplazar con la API de tu app calendario
try:
    from calendario.utils import create_or_update_event_for_medication, delete_event_for_medication
except Exception:
    # Si no existe, definimos stubs para que el código funcione.
    def create_or_update_event_for_medication(medication): pass
    def delete_event_for_medication(medication): pass

@login_required 
def profile_view(request):
    # 1. Acceder al perfil médico del usuario logueado
    # Esto funciona gracias al related_name='medical_profile' en el modelo
    user_profile = request.user.medical_profile

    # Para datos relacionados (ej. medicamentos)
    current_medications = user_profile.medications.all()
    current_allergies = user_profile.allergies.all()
    
    # 2. Manejar la lógica del formulario para guardar datos
    if request.method == 'POST':
        # Asume que MedicalProfileForm se usa para actualizar los campos principales
        form = MedicalProfileForm(request.POST, instance=user_profile)
        
        if form.is_valid():
            form.save() # Guarda los cambios en el perfil del usuario
            # Lógica para guardar/actualizar formularios anidados (Medications, etc.)
            
            # Redirecciona a la misma página o a un mensaje de éxito
            return redirect('nombre_de_la_url_del_perfil') 
    else:
        # Pasa la instancia actual del perfil al formulario para que se precargue con los datos existentes
        form = MedicalProfileForm(instance=user_profile)

    context = {
        'profile_form': form,
        'medications': current_medications,
        'allergies': current_allergies,
        'user': request.user # Para mostrar el nombre de usuario, etc.
    }
    
    return render(request, 'perfil_medico/profile.html', context)

@login_required
def edit_profile(request):
    profile = request.user.medical_profile
    if request.method == 'POST':
        form = MedicalProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('perfil:profile_view')
    else:
        form = MedicalProfileForm(instance=profile)
    return render(request, 'perfil_medico/edit_profile.html', {'form': form})

@login_required
def add_medication(request):
    profile = request.user.medical_profile
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.profile = profile
            med.save()
            # integrar con calendario
            create_or_update_event_for_medication(med)
            return redirect('perfil:profile_view')
    else:
        form = MedicationForm()
    return render(request, 'perfil_medico/add_medication.html', {'form': form})

@login_required
def edit_medication(request, med_id):
    med = get_object_or_404(Medication, pk=med_id, profile=request.user.medical_profile)
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=med)
        if form.is_valid():
            med = form.save()
            create_or_update_event_for_medication(med)
            return redirect('perfil:profile_view')
    else:
        form = MedicationForm(instance=med)
    return render(request, 'perfil_medico/edit_medication.html', {'form': form})

@login_required
def delete_medication(request, med_id):
    med = get_object_or_404(Medication, pk=med_id, profile=request.user.medical_profile)
    if request.method == 'POST':
        delete_event_for_medication(med)
        med.delete()
        return redirect('perfil:profile_view')
    return render(request, 'perfil_medico/confirm_delete_medication.html', {'med': med})

@login_required
def add_labtest(request):
    profile = request.user.medical_profile
    if request.method == 'POST':
        form = LabTestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.profile = profile
            test.save()
            # integrar con calendario: crea evento si next_scheduled_date existe
            # Puedes crear create_or_update_event_for_labtest(test)
            return redirect('perfil:profile_view')
    else:
        form = LabTestForm()
    return render(request, 'perfil_medico/add_labtest.html', {'form': form})
