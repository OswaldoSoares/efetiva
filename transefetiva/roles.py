from rolepermissions.roles import AbstractUserRole

modulo_painel = 'modulo_painel'
modulo_clientes = 'modulo_clientes'
modulo_colaboradores = 'modulo_colaboradores'
modulo_faturamento = 'modulo_faturamento'
modulo_minutas = 'modulo_minutas'
modulo_pagamentos = 'modulo_pagamentos'
modulo_veiculos = 'modulo_veiculos'
modulo_parametros = 'modulo_parametros'
cria_cliente = 'cria_cliente'
edit_cliente = 'edita_cliente'
exclui_cliente = 'exclui_clinte'
email_cliente = 'email_cliente'
telefone_cliente = 'telefone_cliente'
cobranca_cliente = 'cobrança_cliente'
tabela_cliente = 'tabela_cliente'
tabela_veiculo = 'tabela_veiculo'
tabela_perimetro = 'tabela_perimetro'
tabela_capacidade = 'tabela_capacidade'
cria_colaborador = 'cria_colaborador'
edita_colaborador = 'edita_colaborador'
exclui_colaborador = 'exclui_colaborador'
doc_colaborador = 'doc_colaborador'
telefone_colaborador = 'telefone_colaborador'
banco_colaborador = 'banco_colaborador'
faturar_minuta = 'faturar_minuta'
estornar_faturada = 'estornar_faturada'
pagar_faturada = 'pagar_faturada'
estornar_paga = 'estornar_paga'
cria_minuta = 'cria_minuta'
estorna_fechada = 'estorna_fechada'
edita_minuta = 'edita_minuta'
motorista_minuta = 'motorista_minuta'
veiculo_minuta = 'veiculo_minuta'
ajudante_minuta = 'ajudante_minuta'
hora_minuta = 'hora_minuta'
kn_minuta = 'kn_minuta'
despesa_minuta = 'despesa_minuta'
entrega_minuta = 'entrega_minuta'
comentario_minuta = 'comentario_minuta'
finalizar_minuta = 'finalizar_minuta'
demonstrativo_minuta = 'demonstrativo_minuta'
fechar_minuta = 'fechar_minuta'
cria_veiculo = 'cria_veiculo'
edita_veiculo = 'edita_veiculo'
exclui_veiculo = 'exclui_veiculo'


class Diretor(AbstractUserRole):
    available_permissions = {
        modulo_painel: True,
        modulo_clientes: True,
        modulo_colaboradores: True,
        modulo_faturamento: True,
        modulo_minutas: True,
        modulo_pagamentos: True,
        modulo_veiculos: True,
        modulo_parametros: True,
        cria_cliente: True,
        edit_cliente: True,
        exclui_cliente: True,
        email_cliente: True,
        telefone_cliente: True,
        cobranca_cliente: True,
        tabela_cliente: True,
        tabela_veiculo: True,
        tabela_perimetro: True,
        tabela_capacidade: True,
        cria_colaborador: True,
        edita_colaborador: True,
        exclui_colaborador: True,
        doc_colaborador: True,
        telefone_colaborador: True,
        banco_colaborador: True,
        faturar_minuta: True,
        estornar_faturada: True,
        pagar_faturada: True,
        estornar_paga: True,
        cria_minuta: True,
        estorna_fechada: True,
        edita_minuta: True,
        motorista_minuta: True,
        veiculo_minuta: True,
        ajudante_minuta: True,
        hora_minuta: True,
        kn_minuta: True,
        despesa_minuta: True,
        entrega_minuta: True,
        comentario_minuta: True,
        finalizar_minuta: True,
        demonstrativo_minuta: True,
        fechar_minuta: True,
        cria_veiculo: True,
        edita_veiculo: True,
        exclui_veiculo: True,
    }

class Secretaria(AbstractUserRole):
    available_permissions = {
        modulo_painel: True,
        modulo_clientes: True,
        modulo_colaboradores: True,
        modulo_minutas: True,
        modulo_pagamentos: True,
        modulo_veiculos: True,
        cria_cliente: True,
        edit_cliente: True,
        exclui_cliente: True,
        email_cliente: True,
        telefone_cliente: True,
        cobranca_cliente: True,
        cria_colaborador: True,
        edita_colaborador: True,
        exclui_colaborador: True,
        doc_colaborador: True,
        telefone_colaborador: True,
        banco_colaborador: True,
        faturar_minuta: True,
        cria_minuta: True,
        edita_minuta: True,
        motorista_minuta: True,
        veiculo_minuta: True,
        ajudante_minuta: True,
        hora_minuta: True,
        kn_minuta: True,
        despesa_minuta: True,
        entrega_minuta: True,
        comentario_minuta: True,
        finalizar_minuta: True,
        cria_veiculo: True,
        edita_veiculo: True,
        exclui_veiculo: True,
    }

class Motorista(AbstractUserRole):
    available_permissions = {
        modulo_minutas: True,
        hora_minuta: True,
        kn_minuta: True,
        despesa_minuta: True,
        entrega_minuta: True,
        comentario_minuta: True,
        finalizar_minuta: True,
    }
