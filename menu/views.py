from django.shortcuts import render

def menu_view(request):
    return render (request,'menu/menu.html')


