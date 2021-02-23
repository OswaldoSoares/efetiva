from django.urls import path
from .views import index_pagamento

urlpatterns = [
    path('', index_pagamento, name='index_pagamento'),

]
