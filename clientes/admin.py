from django.contrib import admin
from .models import Cliente,\
    FoneContatoCliente,\
    EMailContatoCliente,\
    Cobranca,\
    FormaPagamento,\
    Tabela,\
    TabelaVeiculo,\
    TabelaCapacidade,\
    TabelaPerimetro

admin.site.register(Cliente)
admin.site.register(FoneContatoCliente)
admin.site.register(EMailContatoCliente)
admin.site.register(Cobranca)
admin.site.register(FormaPagamento)
admin.site.register(Tabela)
admin.site.register(TabelaVeiculo)
admin.site.register(TabelaCapacidade)
admin.site.register(TabelaPerimetro)