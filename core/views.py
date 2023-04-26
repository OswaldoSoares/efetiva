from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def index_core(request):
    return render(request, "core/index.html")
