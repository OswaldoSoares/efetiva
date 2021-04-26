from pessoas import facade


def create_context():
    mensalistas = lista_mensaalista_ativos()
    folha = {}
    for itens in mensalistas:
        folha[itens.Nome] = {'Salario': '0.00', 'Liquido': '0.00'}
        salario = facade.get_salario(itens.idPessoal)
        contracheque = facade.get_contrachequereferencia('Abril', '2021', itens.idPessoal)
        if contracheque:
            totais = facade.saldo_contracheque(contracheque[0].idContraCheque)
            folha[itens.Nome]['Salario'] = salario[0].Salario
            folha[itens.Nome]['Liquido'] = totais['Liquido']
    contexto = {'folha': folha}
    return contexto


def lista_mensaalista_ativos():
    return facade.get_pessoal_mensalista_ativo()
