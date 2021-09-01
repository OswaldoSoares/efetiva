from minutas.models import MinutaColaboradores


class MinutaFinanceiro:
    def __init__(self, descricao, chave_descricao, tipo_valor_tabela, valor_tabela, tipo_valor_minuta, valor_minuta):
        self.descricao = descricao
        self.chave_descricao = chave_descricao
        self.valor_tabela = valor_tabela
        self.tipo_valor_tabela = tipo_valor_tabela
        self.valor_minuta = valor_minuta
        self.tipo_valor_minuta = tipo_valor_minuta
        self.saldo = 0.00
        self.checked = False

    def checked_on(self):
        self.checked = True

    def checked_off(self):
        self.checked = False


def get_total_ajudantes(idminuta):
    return MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='AJUDANTE').count()




porcentagem_paga = MinutaFinanceiro('PORCENTAGEM DA NOTA', 'porcentagem', '%', 0.00, 'R$', 0.00)
horas_paga = MinutaFinanceiro('HORAS', 'horas', 'R$', 0.00, 'HS', '00:00')
horasexcede_paga = MinutaFinanceiro('HORAS EXCEDENTE', 'horasexcede', '%', 0.00, 'HS', '00:00')
kilometragem_paga = MinutaFinanceiro('KILOMETRAGEM', 'kilometragem', 'R$', 0.00, 'UN', 0)
entregas_paga = MinutaFinanceiro('ENTREGAS', 'entregas', 'R$', 0.00, 'UN', 0)
entregaskg_paga = MinutaFinanceiro('ENTREGAS KG', 'entregaskg', 'R$', 0.00, 'KG', 0.00)
entregasvolume_paga = MinutaFinanceiro('ENTREGAS VOLUME', 'entregasvolume', 'R$', 0.00, 'UN', 0)
saida_paga = MinutaFinanceiro('SAIDA', 'saida', 'R$', 0.00, '', '')
capacidade_paga = MinutaFinanceiro('CAPACIDADE PESO', 'capacidade', 'R$', 0.00, '', '')
perimetro_paga = MinutaFinanceiro('PERIMETRO', 'perimetro', '%', 0.00, 'R$', 0.00)
pernoite_paga = MinutaFinanceiro('PERNOITE', 'pernoite', '%', 0.00, 'R$', 0.00)
ajudante_paga = MinutaFinanceiro('AJUDANTE', 'ajudante', 'R$', 0.00, 'UN', 0)


itens_paga = list()
itens_paga.append(porcentagem_paga)
itens_paga.append(horas_paga)
itens_paga.append(horasexcede_paga)
itens_paga.append(kilometragem_paga)
itens_paga.append(entregas_paga)
itens_paga.append(entregaskg_paga)
itens_paga.append(entregasvolume_paga)
itens_paga.append(saida_paga)
itens_paga.append(capacidade_paga)
itens_paga.append(perimetro_paga)
itens_paga.append(pernoite_paga)
itens_paga.append(ajudante_paga)

for x in itens_paga:
    print(x.__dict__)

print(itens_paga)
