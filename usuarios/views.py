from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


# Create your views here.
def tela_logout(request):
    return render(request, "usuarios/logout.html")


def cadastra_usuario(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "usuarios/criausuario.html", {"form": form})


def my_403_template(request, exception):
    context = {"exception": exception}
    return render(request, "website/403.html", context, status=403)


def my_404_template(request, exception):
    context = {"exception": exception}
    return render(request, "website/404.html", context, status=404)
