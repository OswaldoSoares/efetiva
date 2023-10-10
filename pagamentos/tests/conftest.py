"""
    Arquivo com fixture utilizadas no testes
"""
import pytest
from django.contrib.auth.models import User


@pytest.fixture
def super_user():
    """
        Cria um super usuário para usar nos testes.
    Returns:
        user

    """
    user = User.objects.create_superuser(
        username="testuser", password="testpassword"
    )
    return user
