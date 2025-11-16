# login/views.py

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from .forms import LoginForm, UserRegistrationForm  # Asegúrate de importar ambos forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Importamos el sistema de mensajes

# --- VISTA DE LOGIN (MEJORADA) ---
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                              username=cd['username'],
                              password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('menu') # Redirige al menú
                else:
                    # Mensaje de error si la cuenta está inactiva
                    messages.error(request, 'Su cuenta está desactivada.')
            else:
                # Mensaje de error si la clave/usuario es incorrecto
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            # Mensaje de error si el formulario no es válido
            messages.error(request, 'Por favor, complete ambos campos.')
            
        # Si algo falla, volvemos a la página de login
        return redirect('login') 
    
    else:
        form = LoginForm()
    
    # Esta línea solo se ejecuta en el GET (cuando se carga la página)
    return render(request, 'login.html', {'form': form})


# --- VISTA DE LOGOUT (MEJORADA) ---
@login_required 
def user_logout(request):
    logout(request)
    messages.success(request, 'Ha cerrado sesión exitosamente.') # Mensaje de éxito
    return redirect('login') 


# --- VISTA DE REDIRECCIÓN (RAÍZ) ---
def index_redirect_view(request):
    """
    Redirige al usuario al menú si está logueado,
    o a la página de login si no lo está.
    """
    if request.user.is_authenticated:
        return redirect('menu') 
    else:
        return redirect('login')

        
# --- VISTA DE REGISTRO (CORREGIDA) ---
def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Crea el nuevo usuario
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            
            # Muestra mensaje de éxito en la página de login
            messages.success(request, '¡Cuenta creada con éxito! Ya puede ingresar.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    # ===================================================
    #   AQUÍ ESTÁ LA CORRECCIÓN:
    #   Quitamos 'login/' de la ruta de la plantilla.
    # ===================================================
    return render(request, 'register.html', {'form': form})