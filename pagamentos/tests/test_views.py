import pytest
from django.test import Client
from django.urls import reverse
from rolepermissions.checkers import has_permission


@pytest.mark.django_db
def test_view_index_pagamento_existe(super_user):
    url = reverse("index_pagamento")
    client = Client()
    client.login(username="testuser", password="testpassword")
    has_perm = has_permission(super_user, "modulo_pagamentos")
    response = client.get(url)
    assert response.status_code == 200 if has_perm else 403
    print(response.status_code)
