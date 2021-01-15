from django.shortcuts import render
from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.
def tela_logout(request):
    return render(request, 'usuarios/logout.html')
