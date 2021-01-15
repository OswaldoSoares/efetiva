from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import tela_logout

urlpatterns = [
    path('login', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout', tela_logout, name='logout'),
    path('sair', auth_views.LogoutView.as_view(), name='sair'),
    path('senha', auth_views.PasswordChangeView.as_view(template_name='usuarios/senha.html',
         success_url=reverse_lazy('index')), name='senha'),
]