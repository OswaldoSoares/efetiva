from django.urls import path
from .views import index_pagamento, teste

urlpatterns = [
    path('', index_pagamento, name='index_pagamento'),
    path('teste', teste, name='teste'),
]
