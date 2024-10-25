"""
serializers.py

Este módulo define classes de serializadores para converter instâncias de
modelos Django em representações JSON e vice-versa. O Django REST Framework
(DRF) é utilizado para facilitar a criação dessas APIs, permitindo a
serialização e deserialização de dados entre o servidor e o cliente.

Serializadores neste módulo são usados para:
    - Validar os dados de entrada enviados pelos clientes para garantir
      que estejam no formato correto antes de serem salvos no banco de dados.
    - Converter instâncias de modelos em formatos serializados (como JSON)
      para enviar como respostas HTTP.
    - Definir regras de como os campos dos modelos Django devem ser
      representados e validados nas APIs REST.

Cada serializador está associado a um modelo específico, definido nos outros
módulos da aplicação Django.

Exemplo:
    from .models import SeuModelo
    from .serializers import SeuModeloSerializer

    class SeuModeloViewSet(viewsets.ModelViewSet):
        queryset = SeuModelo.objects.all()
        serializer_class = SeuModeloSerializer

Dependências:
    - rest_framework.serializers
    - .models

Classes:
    - SeuModeloSerializer
"""
