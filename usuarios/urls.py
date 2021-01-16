from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import tela_logout, cadastra_usuario

urlpatterns = [
    path('cadastrausuario', cadastra_usuario, name='cadastrausuario'),
    path('login', auth_views.LoginView.as_view(template_name='usuarios/login.html', extra_context={
        'titulo': 'LOGIN'}), name='login'),
    path('logout', tela_logout, name='logout'),
    path('sair', auth_views.LogoutView.as_view(), name='sair'),
    path('senha', auth_views.PasswordChangeView.as_view(template_name='usuarios/login.html', extra_context={
        'titulo': 'ALTERAR SENHA ATUAL'}, success_url=reverse_lazy('logout')), name='senha'),
]