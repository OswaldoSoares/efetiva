import calendar
import datetime
import os
from django.db import connection

from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Max
from django.http import JsonResponse
from django.template.loader import render_to_string
from decimal import Decimal
from PIL import Image, ImageDraw
from despesas import facade as facade_multa
from pagamentos import facade as facade_pagamentos
from pagamentos.models import Recibo

from pessoas.forms import CadastraSalario, CadastraVale, CadastraDemissao
from pessoas.models import (
    Aquisitivo,
    DecimoTerceiro,
    Ferias,
    ParcelasDecimoTerceiro,
    Pessoal,
    Salario,
    DocPessoal,
    FonePessoal,
    ContaPessoal,
    Vales,
    ContraCheque,
    ContraChequeItens,
    CartaoPonto,
)
from minutas.models import MinutaColaboradores
from website.facade import converter_mes_ano, nome_curto, extremos_mes

from transefetiva.settings.settings import MEDIA_ROOT

meses = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]
dias = [
    "SEGUNDA-FEIRA",
    "TERÇA-FEIRA",
    "QUARTA-FEIRA",
    "QUINTA-FEIRA",
    "SEXTA-FEIRA",
    "SÁBADO",
    "DOMINGO",
]


class Colaborador:
    def __init__(self, idpes):
        print(len(connection.queries))
        colaborador = Pessoal.objects.get(idPessoal=idpes)
        self.idpes = colaborador.idPessoal
        self.nome = colaborador.Nome
        self.nome_curto = nome_curto(colaborador.Nome)
        self.endereco = colaborador.Endereco
        self.bairro = colaborador.Bairro
        self.cep = colaborador.CEP
        self.endereco_completo = self.get_endereco_completo(self)
        self.cidade = colaborador.Cidade
        self.estado = colaborador.Estado
        self.cidade_estado = self.get_cidade_estado(self)
        self.data_nascimento = colaborador.DataNascimento
        self.mae = colaborador.Mae
        self.pai = colaborador.Pai
        self.categoria = colaborador.Categoria
        self.tipo_pgto = colaborador.TipoPgto
        self.status_pessoal = colaborador.StatusPessoal
        self.data_admissao = colaborador.DataAdmissao
        self.data_completa_ano = self.data_admissao + relativedelta(years=+1, days=-1)
        self.data_demissao = colaborador.DataDemissao
        self.foto = colaborador.Foto
        self.documentos = ColaboradorDocumentos(idpes).docs
        self.telefones = ColaboradorTelefones(idpes).fone
        self.bancos = ColaboradorBancos(idpes).conta
        self.salario = ColaboradorSalario(idpes).salario
        self.decimo_terceiro = self.get_decimo_terceiro(self)
        self.ferias = self.get_ferias(self)
        self.aquisitivo = self.get_aquisitivo(self)
        self.faltas = self.get_faltas_aquisitivo(self)
        self.salario_ferias = self.get_salario_ferias(self)
        print(len(connection.queries))
        # self.meses_ferias = self.get_meses_feiras(self)

    @staticmethod
    def get_endereco_completo(self):
        endereco_completo = ""
        endereco = self.endereco
        bairro = self.bairro
        if endereco:
            endereco_completo = endereco
        if endereco and bairro:
            endereco_completo = endereco_completo + " - " + bairro
        if not endereco and bairro:
            endereco_completo = bairro
        return endereco_completo

    @staticmethod
    def get_cidade_estado(self):
        cidade_estado = ""
        cep = self.cep
        cidade = self.cidade
        estado = self.estado
        if cidade:
            cidade_estado = cidade
        if cidade and estado:
            cidade_estado = cidade_estado + " - " + estado
        if not cidade and estado:
            cidade_estado = estado
        if cep:
            if cidade_estado == "":
                cidade_estado = "CEP: " + cep
            else:
                cidade_estado = cidade_estado + " - CEP: " + cep
        return cidade_estado

    @staticmethod
    def get_decimo_terceiro(self):
        if self.tipo_pgto == "MENSALISTA":
            hoje = datetime.datetime.today()
            decimo_terceiro = DecimoTerceiro.objects.filter(
                idPessoal=self.idpes, Ano=hoje.year
            )
            lista = []
            for i in decimo_terceiro:
                decimo_terceiro_parcelas = list(
                    ParcelasDecimoTerceiro.objects.filter(
                        idDecimoTerceiro=decimo_terceiro[0].idDecimoTerceiro
                    )
                )
                lista.append(
                    {
                        "id_decimo_terceiro": i.idDecimoTerceiro,
                        "ano": i.Ano,
                        "dozeavos": i.Dozeavos,
                        "valor_base": i.ValorBase,
                        "valor": i.Valor,
                        "pago": i.Pago,
                        "parcelas": decimo_terceiro_parcelas,
                    }
                )
        else:
            lista = []
        return lista

    @staticmethod
    def get_ferias(self):
        if self.tipo_pgto == "MENSALISTA":
            ferias = Ferias.objects.filter(idPessoal=self.idpes)
            lista = [
                {
                    "data_inicial": i.DataInicial,
                    "data_final": i.DataFinal,
                    "id_ferias": i.idFerias,
                    "idaquisitivo": i.idAquisitivo_id,
                    "dias": (i.DataFinal - i.DataInicial).days + 1,
                }
                for i in ferias
            ]
        else:
            lista = []
        return lista

    @staticmethod
    def get_aquisitivo(self):
        if self.tipo_pgto == "MENSALISTA":
            salvar = False
            aquisitivo = Aquisitivo.objects.filter(idPessoal=self.idpes).order_by(
                "-DataInicial"
            )
            aquisitivo_inicial = self.data_admissao
            aquisitivo_final = aquisitivo_inicial + relativedelta(years=+1, days=-1)
            if not aquisitivo:
                salvar = True
            else:
                if not self.data_demissao:
                    if aquisitivo[0].DataFinal < datetime.datetime.today().date():
                        aquisitivo_inicial = self.data_admissao + relativedelta(
                            years=+len(aquisitivo)
                        )
                        aquisitivo_final = aquisitivo_inicial + relativedelta(
                            years=+1, days=-1
                        )
                        salvar = True
            if salvar:
                obj = Aquisitivo()
                obj.DataInicial = aquisitivo_inicial
                obj.DataFinal = aquisitivo_final
                obj.idPessoal_id = self.idpes
                obj.save()
                aquisitivo = Aquisitivo.objects.filter(idPessoal=self.idpes).order_by(
                    "-DataInicial"
                )
            lista = [
                {
                    "aquisitivo_inicial": i.DataInicial,
                    "aquisitivo_final": i.DataFinal,
                    "idaquisitivo": i.idAquisitivo,
                }
                for i in aquisitivo
            ]
        else:
            lista = []
        return lista

    @staticmethod
    def get_faltas_aquisitivo(self):
        if self.tipo_pgto == "MENSALISTA":
            inicio = self.aquisitivo[0]["aquisitivo_inicial"]
            final = self.aquisitivo[0]["aquisitivo_final"]
            cartao_ponto = CartaoPonto.objects.filter(
                idPessoal=self.idpes,
                Dia__range=[inicio, final],
                Ausencia="FALTA",
                Remunerado=False,
            )
            lista = [
                datetime.datetime.strftime(i.Dia, "%d/%m/%Y") for i in cartao_ponto
            ]
        else:
            lista = []
        return lista

    @staticmethod
    def get_salario_ferias(self):
        salario = Decimal(self.salario[0]["salario"])
        salario_dia = salario / 30
        faltas = len(self.faltas)
        salario_ferias = Decimal(0.00)
        if faltas < 6:
            salario_ferias = salario
        elif faltas > 5 and faltas < 15:
            salario_ferias = salario_dia * 24
        elif faltas > 14 and faltas < 24:
            salario_ferias = salario_dia * 18
        elif faltas > 23 and faltas < 33:
            salario_ferias = salario_dia * 12
        salario_ferias = round(salario_ferias, 2)
        return salario_ferias


class ColaboradorDocumentos:
    def __init__(self, idpes):
        self.docs = self.get_docpessoal(idpes)

    @staticmethod
    def get_docpessoal(idpes):
        documentos = DocPessoal.objects.filter(idPessoal=idpes)
        lista = [
            {
                "iddoc": i.idDocPessoal,
                "tipo": i.TipoDocumento,
                "documento": i.Documento,
                "data_doc": i.Data,
            }
            for i in documentos
        ]
        return lista


class ColaboradorTelefones:
    def __init__(self, idpes):
        self.fone = self.get_telefones(idpes)

    @staticmethod
    def get_telefones(idpes):
        telefones = FonePessoal.objects.filter(idPessoal=idpes)
        lista = [
            {
                "idfone": i.idFonePessoal,
                "tipo": i.TipoFone,
                "fone": i.Fone,
                "contato": i.Contato,
            }
            for i in telefones
        ]
        return lista


class ColaboradorBancos:
    def __init__(self, idpes):
        self.conta = self.get_bancos(idpes)

    @staticmethod
    def get_bancos(idpes):
        bancos = ContaPessoal.objects.filter(idPessoal=idpes)
        lista = [
            {
                "idconta": i.idContaPessoal,
                "banco": i.Banco,
                "agencia": i.Agencia,
                "conta": i.Conta,
                "tipo": i.TipoConta,
                "titular": i.Titular,
                "documento": i.Documento,
                "pix": i.PIX,
            }
            for i in bancos
        ]
        return lista


class ColaboradorSalario:
    def __init__(self, idpes):
        self.salario = self.get_salario(idpes)

    @staticmethod
    def get_salario(idpes):
        valores = Salario.objects.filter(idPessoal=idpes)
        lista = [
            {
                "idsalario": i.idSalario,
                "salario": i.Salario,
                "transporte": i.ValeTransporte,
            }
            for i in valores
        ]
        return lista


def create_pessoal_context(idpessoa: int):
    colaborador = get_pessoal(idpessoa)
    docpessoa = get_docpessoal(idpessoa)
    fonepessoa = get_fonepessoal(idpessoa)
    contapessoa = get_contapessoal(idpessoa)
    contracheque = get_contracheque(idpessoa)
    salario = get_salario(idpessoa)
    instance_colaborador = get_pessoal(idpessoa).first()
    instance_salario = get_salario(idpessoa).first()
    formsalario = CadastraSalario(instance=instance_salario)
    formvale = CadastraVale()
    form_demissao = CadastraDemissao(instance=instance_colaborador)
    minutas = MinutaColaboradores.objects.filter(idPessoal=idpessoa)
    context = {
        "colaborador": colaborador,
        "docpessoa": docpessoa,
        "fonepessoa": fonepessoa,
        "contapessoa": contapessoa,
        "contracheque": contracheque,
        "salario": salario,
        "formsalario": formsalario,
        "formvale": formvale,
        "form_demissao": form_demissao,
        "minutas": minutas,
    }
    return context


def list_pessoal_all():
    return list(Pessoal.objects.all())


def get_pessoal_all():
    return Pessoal.objects.all()


def get_pessoal_mensalista_ativo():
    return Pessoal.objects.filter(TipoPgto="MENSALISTA", StatusPessoal=True)


def get_pessoal_nao_mensalista_ativo():
    return Pessoal.objects.filter(StatusPessoal=True).exclude(TipoPgto="MENSALISTA")


def get_pessoal(idpessoa: int):
    colaborador = Pessoal.objects.filter(idPessoal=idpessoa)
    return colaborador


def get_docpessoal(idpessoa: int):
    docpessoal = DocPessoal.objects.filter(idPessoal=idpessoa)
    return docpessoal


def get_fonepessoal(idpessoa: int):
    fonepessoal = FonePessoal.objects.filter(idPessoal=idpessoa)
    return fonepessoal


def get_contapessoal(idpessoa: int):
    contapessoal = ContaPessoal.objects.filter(idPessoal=idpessoa)
    return contapessoal


def get_salario(idpessoal: int):
    salario = Salario.objects.filter(idPessoal=idpessoal)
    return salario


def get_contracheque(idpessoal: int):
    contracheque = ContraCheque.objects.filter(idPessoal=idpessoal)
    return contracheque


def get_contrachequeid(idcontracheque: int):
    contracheque = ContraCheque.objects.filter(idContraCheque=idcontracheque)
    return contracheque


def get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia) - 1]
    contracheque = ContraCheque.objects.filter(
        MesReferencia=mes, AnoReferencia=anoreferencia, idPessoal=idpessoal
    )
    return contracheque


def get_contracheque_itens(idcontracheque: int):
    contracheque_itens = ContraChequeItens.objects.filter(
        idContraCheque_id=idcontracheque
    ).order_by("Registro")
    return contracheque_itens


def save_salario(idpessoal, salario, horasmensais, valetransporte):
    try:
        qs_salario = Salario.objects.get(idPessoal_id=idpessoal)
        obj = Salario(qs_salario)
        obj.idSalario = qs_salario.idSalario
        obj.Salario = salario
        obj.HorasMensais = horasmensais
        obj.ValeTransporte = valetransporte
        obj.idPessoal_id = idpessoal
    except Salario.DoesNotExist:
        obj = Salario()
        obj.Salario = salario
        obj.HorasMensais = horasmensais
        obj.ValeTransporte = valetransporte
        obj.idPessoal_id = idpessoal
    obj.save()


def edita_data_demissao(idpessoal, data_demissao):
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    obj = colaborador
    obj.DataDemissao = data_demissao
    obj.save(update_fields=["DataDemissao"])


def create_vale(data, descricao, valor, idpessoal):
    obj = Vales()
    obj.Data = data
    obj.Descricao = descricao
    obj.Valor = valor
    obj.idPessoal_id = idpessoal
    obj.save()


def create_contracheque(mesreferencia, anoreferencia, valor, idpessoal):
    colaborador = get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month:
            salario = get_salario(idpessoal)
            if not busca_contracheque(
                meses[int(mesreferencia) - 1], anoreferencia, idpessoal
            ):
                obj = ContraCheque()
                obj.MesReferencia = meses[int(mesreferencia) - 1]
                obj.AnoReferencia = anoreferencia
                obj.Valor = valor
                obj.idPessoal_id = idpessoal
                obj.save()
                create_contracheque_itens(
                    "Salario", salario[0].Salario, "C", obj.idContraCheque
                )


def create_contracheque_itens(descricao, valor, registro, idcontracheque):
    if float(valor) > 0:
        if not busca_contrachequeitens(idcontracheque, descricao, registro):
            obj = ContraChequeItens()
            obj.Descricao = descricao
            obj.Valor = valor
            obj.Registro = registro
            obj.idContraCheque_id = idcontracheque
            obj.save()


def altera_contracheque_itens(contrachequeitens, valorhoraextra):
    if float(valorhoraextra) > 0:
        obj = contrachequeitens
        obj.Valor = valorhoraextra
        obj.save(update_fields=["Valor"])


def busca_contracheque(mesreferencia, anoreferencia, idpessoal):
    qs_contracheque = ContraCheque.objects.filter(
        MesReferencia=mesreferencia, AnoReferencia=anoreferencia, idPessoal=idpessoal
    )
    if qs_contracheque:
        return True


def busca_contrachequeitens(idcontracheque, descricao, registro):
    contrachequeitens = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Descricao=descricao, Registro=registro
    )
    return contrachequeitens


def saldo_contracheque(idcontracheque):
    credito = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Registro="C"
    ).aggregate(Total=Sum("Valor"))
    debito = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Registro="D"
    ).aggregate(Total=Sum("Valor"))
    if not credito["Total"]:
        credito["Total"] = Decimal("0.00")
    if not debito["Total"]:
        debito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito["Total"],
        "Liquido": credito["Total"] - debito["Total"],
    }
    return totais


def print_contracheque_context(idcontracheque):
    contracheque = get_contrachequeid(idcontracheque)
    contrachequeitens = get_contracheque_itens(idcontracheque)
    colaborador = get_pessoal(contracheque[0].idPessoal_id)
    credito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque, Registro="C"
    ).aggregate(Total=Sum("Valor"))
    debito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque, Registro="D"
    ).aggregate(Total=Sum("Valor"))
    if credito["Total"]:
        credito["Total"] = Decimal("0.00")
    if debito["Total"]:
        debito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito["Total"],
        "Liquido": credito["Total"] - debito["Total"],
    }
    contexto = {
        "contracheque": contracheque,
        "contrachequeitens": contrachequeitens,
        "colaborador": colaborador,
        "totais": totais,
    }
    return contexto


def create_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    colaborador = get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month:
            admissao = datetime.datetime(admissao.year, admissao.month, admissao.day)
            if not busca_cartaoponto_referencia(
                mesreferencia, anoreferencia, idpessoal
            ):
                referencia = calendar.monthrange(int(anoreferencia), int(mesreferencia))
                for x in range(1, referencia[1] + 1):
                    dia = "{}-{}-{}".format(anoreferencia, mesreferencia, x)
                    dia = datetime.datetime.strptime(dia, "%Y-%m-%d")
                    obj = CartaoPonto()
                    obj.Dia = dia
                    obj.Entrada = "07:00"
                    obj.Saida = "17:00"
                    if dia.weekday() == 5 or dia.weekday() == 6:
                        obj.Ausencia = dias[dia.weekday()]
                    else:
                        obj.Ausencia = ""
                    if dia < admissao:
                        obj.Ausencia = "-------"
                    obj.idPessoal_id = idpessoal
                    obj.save()


def busca_cartaoponto_referencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = meses.index(mesreferencia) + 1
    else:
        mes = int(mesreferencia)
    dia = "{}-{}-{}".format(anoreferencia, mes, 1)
    dia = datetime.datetime.strptime(dia, "%Y-%m-%d")
    referencia = calendar.monthrange(int(anoreferencia), mes)
    diafinal = "{}-{}-{}".format(anoreferencia, mes, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, "%Y-%m-%d")
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    if cartaoponto:
        return cartaoponto


def form_pessoa(request, c_form, c_idobj, c_url, c_view, idpessoal):
    data = dict()
    c_instance = None
    if c_view == "edita_pessoa" or c_view == "exclui_pessoa":
        if c_idobj:
            c_instance = Pessoal.objects.get(idPessoal=c_idobj)
    if request.method == "POST":
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            save_id = form.save()
            if c_view == "cria_pessoa" or c_view == "edita_pessoa":
                data["save_id"] = save_id.idPessoal
                if c_view == "cria_pessoa":
                    save_salario(save_id.idPessoal, 0.00, 1, 0.00)
            else:
                data["save_id"] = save_id.idPessoal_id
        else:
            pass
    else:
        form = c_form(instance=c_instance)
    context = {
        "form": form,
        "c_idobj": c_idobj,
        "c_url": c_url,
        "c_view": c_view,
        "idpessoal": idpessoal,
    }
    data["html_form"] = render_to_string(
        "pessoas/formpessoa.html", context, request=request
    )
    data["c_view"] = c_view
    c_return = JsonResponse(data)
    return c_return


def form_exclui_pessoal(request, c_idobj, c_url, c_view, idpessoal):
    data = dict()
    c_queryset = None
    if c_view == "exclui_pessoa":
        c_queryset = Pessoal.objects.get(idPessoal=c_idobj)
    # elif c_view == 'exclui_email_cliente':
    #     c_queryset = EMailContatoCliente.objects.get(idEmailContatoCliente=c_idobj)
    # elif c_view == 'exclui_fone_cliente':
    #     c_queryset = FoneContatoCliente.objects.get(idFoneContatoCliente=c_idobj)
    # elif c_view == 'exclui_cobranca_cliente':
    #     c_queryset = Cobranca.objects.get(idCobranca=c_idobj)
    # elif c_view == 'exclui_tabela_capacidade':
    #     c_queryset = TabelaCapacidade.objects.get(idTabelaCapacidade=c_idobj)
    # elif c_view == 'exclui_tabela_perimetro':
    #     c_queryset = TabelaPerimetro.objects.get(idTabelaPerimetro=c_idobj)
    if request.method == "POST":
        c_queryset.delete()
    context = {
        "c_url": c_url,
        "c_view": c_view,
        "c_queryset": c_queryset,
        "idpessoal": idpessoal,
    }
    data["html_form"] = render_to_string(
        "pessoas/formpessoa.html", context, request=request
    )
    data["c_view"] = c_view
    data["save_id"] = idpessoal
    c_return = JsonResponse(data)
    return c_return


# TODO: Refatoração
def create_contexto_colaboradores_ativo(status_colaborador):
    colaboradores = Pessoal.objects.filter(StatusPessoal=status_colaborador)
    lista = []
    hoje = datetime.datetime.today()
    for i in colaboradores:
        decimo_terceiro = DecimoTerceiro.objects.filter(
            idPessoal=i.idPessoal, Ano=hoje.year
        )
        lista.append(
            {
                "idpessoal": i.idPessoal,
                "nome": i.Nome,
                "nome_curto": nome_curto(i.Nome),
                "tipo_pgto": i.TipoPgto,
                "status_pessoal": i.StatusPessoal,
                "decimo_terceiro": decimo_terceiro,
            }
        )
    return lista


def create_data_lista_colaboradores_ativo(request, contexto):
    data = dict()
    html_lista_colaboradores_ativo(request, contexto, data)
    return JsonResponse(data)


def html_lista_colaboradores_ativo(request, contexto, data):
    data["html_lista_colaboradores_ativo"] = render_to_string(
        "pessoas/html_lista_colaboradores.html", contexto, request=request
    )
    return data


def create_recibos_colaborador(idpessoal):
    recibos = Recibo.objects.filter(idPessoal_id=idpessoal).order_by(
        "-DataRecibo", "-Recibo"
    )
    return {"recibos": recibos}


def html_recibos_colaborador(request, contexto, data):
    idpessoal = contexto["colaborador"]["idpes"]
    recibos = create_recibos_colaborador(idpessoal)
    contexto.update(recibos)
    data["html_recibos_colaborador"] = render_to_string(
        "pagamentos/reciboavulso.html", contexto, request=request
    )
    return data


def create_contexto_consulta_colaborador(idpessoal):
    colaborador = Colaborador(idpessoal).__dict__
    multas = facade_multa.multas_pagar("MOTORISTA", idpessoal)
    return {"colaborador": colaborador, "multas": multas}


def create_data_consulta_colaborador(request, contexto):
    tipo_pgto = contexto["colaborador"]["tipo_pgto"]
    data = dict()
    html_lista_colaboradores_ativo(request, contexto, data)
    html_dados_colaborador(request, contexto, data)
    if tipo_pgto == "MENSALISTA":
        html_ferias_colaborador(request, contexto, data)
        html_decimo_terceiro(request, contexto, data)
    else:
        html_recibos_colaborador(request, contexto, data)
    html_multas_colaborador(request, contexto, data)
    return JsonResponse(data)


def html_ferias_colaborador(request, contexto, data):
    data["html_ferias_colaborador"] = render_to_string(
        "pessoas/html_ferias_colaborador.html", contexto, request=request
    )
    return data


def html_multas_colaborador(request, contexto, data):
    data["html_multas_colaborador"] = render_to_string(
        "pessoas/html_multas_colaborador.html", contexto, request=request
    )
    return data


def html_dados_colaborador(request, contexto, data):
    data["html_dados_colaborador"] = render_to_string(
        "pessoas/html_dados_colaborador.html", contexto, request=request
    )
    data["tipo_pgto"] = contexto["colaborador"]["tipo_pgto"]
    return data


def html_decimo_terceiro(request, contexto, data):
    data["html_decimo_terceiro"] = render_to_string(
        "pessoas/html_decimo_terceiro.html", contexto, request=request
    )
    return data


def salva_foto_colaborador(idpessoal, arquivo):
    obj = Pessoal.objects.get(idPessoal=idpessoal)
    if obj.Foto:
        file = f"{MEDIA_ROOT}/{obj.Foto}"
        if os.path.isfile(file):
            os.remove(file)
    obj.Foto = arquivo
    obj.save(update_fields=["Foto"])
    return obj


def gera_decimo_terceiro():
    colaboradores = Pessoal.objects.filter(
        TipoPgto="MENSALISTA", StatusPessoal=True, DataDemissao__isnull=True
    )
    hoje = datetime.datetime.today()
    for x in colaboradores:
        colaborador_decimo = DecimoTerceiro.objects.filter(
            idPessoal=x.idPessoal, Ano=hoje.year
        )
        if not colaborador_decimo:
            salario = Salario.objects.get(idPessoal=x.idPessoal)
            admissao = x.DataAdmissao
            if admissao.year < hoje.year:
                avos = 12
            else:
                avos = 12 - admissao.month
                if admissao.day < 17:
                    avos += 1
            valor = salario.Salario / 12 * avos
            obj = DecimoTerceiro()
            obj.Ano = hoje.year
            obj.ValorBase = salario.Salario
            obj.Dozeavos = avos
            obj.Valor = valor
            obj.idPessoal_id = x.idPessoal
            obj.save()
            new_obj = obj.idDecimoTerceiro
            gera_decimo_terceiro_parcelas(new_obj, valor)


def gera_decimo_terceiro_parcelas(idDecimoTerceiro, valor):
    for i in range(1, 3):
        obj = ParcelasDecimoTerceiro()
        obj.Valor = round(valor / 2, 2)
        obj.Parcela = i
        obj.idDecimoTerceiro_id = idDecimoTerceiro
        obj.save()


def atualiza_decimno_terceito_parcelas(idDecimoTerceiro):
    pass


def create_contexto_print_decimo_terceiro(idpes, idparcela):
    colaborador = Colaborador(idpes).__dict__
    contexto = {"colaborador": colaborador, "idparcela": idparcela}
    return contexto


def create_contexto_verbas_rescisoria(colaborador):
    aquisitvo = (
        Aquisitivo.objects.filter(idPessoal=colaborador["idpes"])
        .order_by("-DataInicial")
        .first()
    )
    meses_ferias = rescisao_ferias_meses(aquisitvo.DataInicial, aquisitvo.DataFinal)
    meses_decimo_terceiro = rescisao_descimo_terceiro_meses(aquisitvo.DataFinal)
    rescisao_salario = colaborador["salario"][0]["salario"]
    rescisao_ferias = rescisao_salario / 12 * meses_ferias
    rescisao_terco_ferias = rescisao_ferias / 3
    rescisao_descimo_terceiro = rescisao_salario / 12 * meses_decimo_terceiro
    _mes_ano = datetime.datetime.strftime(colaborador["data_demissao"], "%B/%Y")
    folha = facade_pagamentos.create_contexto_funcionario(
        _mes_ano, colaborador["idpes"]
    )
    rescisao = [
        {
            "salario": round(rescisao_salario, 2),
            "ferias": round(rescisao_ferias, 2),
            "terco_ferias": round(rescisao_terco_ferias, 2),
            "decimo_terceiro": round(rescisao_descimo_terceiro, 2),
            "folha_contra_cheque_itens": folha["contra_cheque_itens"],
        }
    ]
    return {"rescisao": rescisao}


def create_data_verbas_rescisoria(request, contexto):
    data = dict()
    html_verbas_rescisoria(request, contexto, data)
    return JsonResponse(data)


def html_verbas_rescisoria(request, contexto, data):
    data["html_verbas_rescisoria"] = render_to_string(
        "pessoas/html_verbas_rescisoria.html", contexto, request=request
    )
    return data


def rescisao_ferias_meses(data_inicial, data_final):
    dia_inicial = data_inicial.day
    if dia_inicial < 16:
        mes_inicial = data_inicial.month
    else:
        mes_inicial = data_inicial.month + 1
    dia_final = data_final.day
    if dia_final > 14:
        mes_final = data_final.month
    else:
        mes_final = data_final.month - 1
    meses = 12 - mes_inicial + 1 + mes_final
    return meses


def rescisao_descimo_terceiro_meses(data_final):
    dia_final = data_final.day
    if dia_final > 14:
        mes_final = data_final.month
    else:
        mes_final = data_final.month - 1
    meses = mes_final
    return meses


def create_data_form_adiciona_documento_colaborador(request, contexto):
    data = dict()
    html_form_adiciona_documento_colaborador(request, contexto, data)
    return JsonResponse(data)


def create_data_form_exclui_documento_colaborador(request, contexto):
    data = dict()
    html_form_confirma_exclusao(request, contexto, data)
    return JsonResponse(data)


def html_form_adiciona_documento_colaborador(request, contexto, data):
    data["html_form_documento_colaborador"] = render_to_string(
        "pessoas/html_form_documento_colaborador.html", contexto, request=request
    )
    return data


def html_form_confirma_exclusao(request, contexto, data):
    data["html_form_confirma_exclusao"] = render_to_string(
        "pessoas/html_form_confirma_exclusao.html", contexto, request=request
    )
    return data


def valida_documento_colaborador(request):
    msg = dict()
    error = False
    seleciona = request.POST.get("tipo_doc")
    if seleciona == "0":
        msg["erro_tipo_doc"] = "Obrigatório selecionar o tipo de documento."
        error = True
    documento = request.POST.get("numero_doc")
    if documento == "":
        msg["erro_documento"] = "Obrigatório digitar o número do documento."
        error = True
    elif len(documento) < 4:
        msg["erro_documento"] = "Número de documento inválido."
        error = True
    return error, msg


def read_documento_post(request):
    documento_post = dict()
    documento_post["tipo_doc"] = request.POST.get("tipo_doc")
    documento_post["numero_doc"] = request.POST.get("numero_doc")
    documento_post["data_doc"] = request.POST.get("data_doc")
    documento_post["idpessoal"] = request.POST.get("idpessoal")
    return documento_post


def read_documento_database(iddocpessoal):
    documento = DocPessoal.objects.get(idDocPessoal=iddocpessoal)
    documento_database = dict()
    documento_database["tipo_doc"] = documento.TipoDocumento
    documento_database["numero_doc"] = documento.Documento
    documento_database["data_doc"] = datetime.datetime.strftime(
        documento.Data, "%Y-%m-%d"
    )
    documento_database["idpessoal"] = documento.idPessoal_id
    documento_database["iddocpessoal"] = documento.idDocPessoal
    return documento_database


def salva_documento(documento):
    obj = DocPessoal()
    obj.TipoDocumento = documento["tipo_doc"]
    obj.Documento = documento["numero_doc"]
    obj.Data = documento["data_doc"]
    obj.idPessoal_id = documento["idpessoal"]
    obj.save()


def altera_documento(documento, iddocpessoal):
    doc = DocPessoal.objects.get(idDocPessoal=iddocpessoal)
    obj = DocPessoal(doc)
    obj.idDocPessoal = doc.idDocPessoal
    obj.TipoDocumento = documento["tipo_doc"]
    obj.Documento = documento["numero_doc"]
    obj.Data = documento["data_doc"]
    obj.idPessoal_id = documento["idpessoal"]
    obj.save()


def create_contexto_exclui_documento_colaborador(iddocpessoal):
    documento = DocPessoal.objects.get(idDocPessoal=iddocpessoal)
    tipo = documento.TipoDocumento
    doc = documento.Documento
    idpessoal = documento.idPessoal_id
    mensagem = f"Confirma a exclusão do documento: {tipo} de número {doc}?"
    js_class = "js-apaga-documento"
    return {
        "mensagem": mensagem,
        "idobj": iddocpessoal,
        "idpessoal": idpessoal,
        "js_class": js_class,
    }


def apaga_documento(iddocpessoal):
    documento = DocPessoal.objects.get(idDocPessoal=iddocpessoal)
    documento.delete()


def create_data_form_adiciona_fone_colaborador(request, contexto):
    data = dict()
    html_form_adiciona_fone_colaborador(request, contexto, data)
    return JsonResponse(data)


# TODO renomear função já existe fazendo a mesma função.
def create_data_form_exclui_fone_colaborador(request, contexto):
    data = dict()
    html_form_confirma_exclusao(request, contexto, data)
    return JsonResponse(data)


def html_form_adiciona_fone_colaborador(request, contexto, data):
    data["html_form_fone_colaborador"] = render_to_string(
        "pessoas/html_form_telefone_colaborador.html", contexto, request=request
    )
    return data


def valida_fone_colaborador(request):
    msg = dict()
    error = False
    seleciona = request.POST.get("tipo_fone")
    if seleciona == "0":
        msg["erro_tipo_fone"] = "Obrigatório selecionar o tipo de telefone."
        error = True
    telefone = request.POST.get("numero_fone")
    if telefone == "":
        msg["erro_telefone"] = "Obrigatório digitar o número do telefone."
        error = True
    elif len(telefone) < 8:
        msg["erro_telefone"] = "Número de telefone inválido."
        error = True
    return error, msg


def read_fone_post(request):
    fone_post = dict()
    fone_post["tipo_fone"] = request.POST.get("tipo_fone")
    fone_post["numero_fone"] = request.POST.get("numero_fone")
    fone_post["contato"] = request.POST.get("contato")
    fone_post["idpessoal"] = request.POST.get("idpessoal")
    return fone_post


def read_fone_database(idfonepessoal):
    fone = FonePessoal.objects.get(idFonePessoal=idfonepessoal)
    fone_database = dict()
    fone_database["tipo_fone"] = fone.TipoFone
    fone_database["numero_fone"] = fone.Fone
    fone_database["contato"] = fone.Contato
    fone_database["idpessoal"] = fone.idPessoal_id
    fone_database["idfonepessoal"] = fone.idFonePessoal
    return fone_database


def salva_fone(fone):
    obj = FonePessoal()
    obj.TipoFone = fone["tipo_fone"]
    obj.Fone = fone["numero_fone"]
    obj.Contato = fone["contato"]
    obj.idPessoal_id = fone["idpessoal"]
    obj.save()


def altera_fone(fone, idfonepessoal):
    telefone = FonePessoal.objects.get(idFonePessoal=idfonepessoal)
    obj = FonePessoal(telefone)
    obj.idFonePessoal = telefone.idFonePessoal
    obj.TipoFone = fone["tipo_fone"]
    obj.Fone = fone["numero_fone"]
    obj.Contato = fone["contato"]
    obj.idPessoal_id = fone["idpessoal"]
    obj.save()


def create_contexto_exclui_fone_colaborador(idfonepessoal):
    fone = FonePessoal.objects.get(idFonePessoal=idfonepessoal)
    tipo = fone.TipoFone
    telefone = fone.Fone
    idpessoal = fone.idPessoal_id
    mensagem = f"Confirma a exclusão do telefone: {tipo} de número {telefone}?"
    js_class = "js-apaga-telefone"
    return {
        "mensagem": mensagem,
        "idobj": idfonepessoal,
        "idpessoal": idpessoal,
        "js_class": js_class,
    }


def apaga_fone(idfonepessoal):
    fone = FonePessoal.objects.get(idFonePessoal=idfonepessoal)
    fone.delete()


def create_data_form_adiciona_conta_colaborador(request, contexto):
    data = dict()
    html_form_adiciona_conta_colaborador(request, contexto, data)
    return JsonResponse(data)


# TODO renomear função já existe fazendo a mesma função.
def create_data_form_exclui_conta_colaborador(request, contexto):
    data = dict()
    html_form_confirma_exclusao(request, contexto, data)
    return JsonResponse(data)


# TODO renomear função já existe fazendo a mesma função.
def create_data_form_exclui_periodo_ferias(request, contexto):
    data = dict()
    html_form_confirma_exclusao(request, contexto, data)
    return JsonResponse(data)


def html_form_adiciona_conta_colaborador(request, contexto, data):
    data["html_form_conta_colaborador"] = render_to_string(
        "pessoas/html_form_conta_colaborador.html", contexto, request=request
    )
    return data


def valida_conta_colaborador(request):
    msg = dict()
    error = False
    banco = request.POST.get("banco")
    pix = request.POST.get("pix")
    if banco == "" and pix == "":
        msg["erro_banco"] = "Obrigatório digitar o nome do banco."
        msg["erro_pix"] = "Obrigatório digitar a chave PIX."
        error = True
    if banco != "" and len(banco) < 2:
        msg["erro_banco"] = "Nome do banco inválido."
        error = True
    if pix != "" and len(pix) < 6:
        msg["erro_pix"] = "Chave PIX inválida."
        error = True
    agencia = request.POST.get("agencia")
    if banco != "" and agencia == "":
        msg["erro_agencia"] = "Obrigatório digitar o número da agência."
        error = True
    if agencia != "" and len(agencia) < 3:
        msg["erro_agencia"] = "Número da agência inválida."
        error = True
    conta = request.POST.get("conta")
    if banco != "" and conta == "":
        msg["erro_numero_conta"] = "Obrigatório digitar o número da conta."
        error = True
    if conta != "" and len(conta) < 4:
        msg["erro_numero_conta"] = "Número da conta inválida."
        error = True
    seleciona = request.POST.get("tipo_conta")
    if banco != "" and seleciona == "0":
        msg["erro_tipo_conta"] = "Obrigatório selecionar o tipo de conta."
        error = True
    return error, msg


def read_conta_post(request):
    conta_post = dict()
    conta_post["banco"] = request.POST.get("banco")
    conta_post["agencia"] = request.POST.get("agencia")
    conta_post["conta"] = request.POST.get("conta")
    conta_post["tipo_conta"] = request.POST.get("tipo_conta")
    conta_post["titular"] = request.POST.get("titular")
    conta_post["documento"] = request.POST.get("documento")
    conta_post["pix"] = request.POST.get("pix")
    conta_post["idpessoal"] = request.POST.get("idpessoal")
    return conta_post


def read_conta_database(idcontapessoal):
    conta = ContaPessoal.objects.get(idContaPessoal=idcontapessoal)
    conta_database = dict()
    conta_database["banco"] = conta.Banco
    conta_database["agencia"] = conta.Agencia
    conta_database["conta"] = conta.Conta
    conta_database["tipo_conta"] = conta.TipoConta
    conta_database["titular"] = conta.Titular
    conta_database["documento"] = conta.Documento
    conta_database["pix"] = conta.PIX
    conta_database["idpessoal"] = conta.idPessoal_id
    conta_database["idcontapessoal"] = conta.idContaPessoal
    return conta_database


def salva_conta(conta):
    obj = ContaPessoal()
    obj.Banco = conta["banco"]
    obj.Agencia = conta["agencia"]
    obj.Conta = conta["conta"]
    obj.TipoConta = conta["tipo_conta"]
    obj.Titular = conta["titular"]
    obj.Documento = conta["documento"]
    obj.PIX = conta["pix"]
    obj.idPessoal_id = conta["idpessoal"]
    obj.save()


def altera_conta(conta, idcontapessoal):
    conta_banco = ContaPessoal.objects.get(idContaPessoal=idcontapessoal)
    obj = ContaPessoal(conta_banco)
    obj.idContaPessoal = conta_banco.idContaPessoal
    obj.Banco = conta["banco"]
    obj.Agencia = conta["agencia"]
    obj.Conta = conta["conta"]
    obj.TipoConta = conta["tipo_conta"]
    obj.Titular = conta["titular"]
    obj.Documento = conta["documento"]
    obj.PIX = conta["pix"]
    obj.idPessoal_id = conta["idpessoal"]
    obj.save()


def create_contexto_exclui_conta_colaborador(idcontapessoal):
    conta = ContaPessoal.objects.get(idContaPessoal=idcontapessoal)
    banco = conta.Banco
    agencia = conta.Agencia
    conta_banco = conta.Conta
    pix = conta.PIX
    idpessoal = conta.idPessoal_id
    if conta_banco:
        mensagem = f"Confirma a exclusão da conta: {banco} - AG: {agencia} Conta: {conta_banco}?"
    else:
        mensagem = f"Confirma a exclusão da conta: Chave PIX: {pix}?"
    js_class = "js-apaga-conta"
    return {
        "mensagem": mensagem,
        "idobj": idcontapessoal,
        "idpessoal": idpessoal,
        "js_class": js_class,
    }


def create_contexto_exclui_ferias(idferias):
    ferias = Ferias.objects.get(idFerias=idferias)
    inicio = datetime.datetime.strftime(ferias.DataInicial, "%d/%m/%Y")
    final = datetime.datetime.strftime(ferias.DataFinal, "%d/%m/%Y")
    idpessoal = ferias.idPessoal_id
    mensagem = f"Confirma a exclusão do periodo de férias de: {inicio} - {final}?"
    js_class = "js-exclui-periodo-ferias"
    return {
        "mensagem": mensagem,
        "idobj": idferias,
        "idpessoal": idpessoal,
        "js_class": js_class,
    }


def exclui_periodo_ferias_base_dados(idferias):
    ferias = Ferias.objects.get(idFerias=idferias)
    ferias.delete()


def apaga_conta(idcontapessoal):
    conta = ContaPessoal.objects.get(idContaPessoal=idcontapessoal)
    conta.delete()


def create_data_form_paga_decimo_terceiro(request, contexto):
    data = dict()
    html_form_paga_decimo_terceiro(request, contexto, data)
    return JsonResponse(data)


def html_form_paga_decimo_terceiro(request, contexto, data):
    data["html_form_paga_decimo_terceiro"] = render_to_string(
        "pessoas/html_form_paga_decimo_terceiro.html", contexto, request=request
    )
    return data


def paga_parcela(idparcela, data_pgto):
    obj = ParcelasDecimoTerceiro.objects.get(idParcelasDecimoTerceiro=idparcela)
    obj.DataPgto = data_pgto
    obj.Pago = True
    obj.save(update_fields=["DataPgto", "Pago"])


# Deixa a imagem circular e salva como png, utilizada na impressão da ficha cadastral
def prepare_mask(size, antialias=2):
    mask = Image.new("L", (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)


def crop(im, s):
    w, h = im.size
    k = w / s[0] - h / s[1]
    if k > 0:
        im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif k < 0:
        im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)


def do_crop(img):
    size = (200, 200)
    im = Image.open(img)
    im = crop(im, size)
    im.putalpha(prepare_mask(size, 4))
    output = str(img).replace("jpg", "png").replace("jpeg", "png")
    im.save(output)
    return output


def create_data_form_salario_colaborador(request, contexto):
    data = dict()
    html_form_salario_colaborador(request, contexto, data)
    return JsonResponse(data)


def html_form_salario_colaborador(request, contexto, data):
    data["html_form_salario_colaborador"] = render_to_string(
        "pessoas/html_form_salario_colaborador.html", contexto, request=request
    )
    return data


def valida_salario_colaborador(request):
    msg = dict()
    error = False
    salario = float(request.POST.get("valor_salario"))
    if salario < 1.00:
        msg["erro_salario"] = "O salário deve ser maior que R$ 0,99."
        error = True
    return error, msg


def read_salario_post(request):
    conta_post = dict()
    conta_post["salario"] = request.POST.get("valor_salario")
    conta_post["transporte"] = request.POST.get("valor_transporte")
    conta_post["idpessoal"] = request.POST.get("idpessoal")
    conta_post["idsalario"] = request.POST.get("idsalario")
    return conta_post


def read_salario_database(idpessoal):
    salario = Salario.objects.get(idPessoal=idpessoal)
    conta_database = dict()
    conta_database["salario"] = str(salario.Salario)
    conta_database["transporte"] = str(salario.ValeTransporte)
    conta_database["idpessoal"] = salario.idPessoal
    conta_database["idsalario"] = salario.idSalario
    return conta_database


def altera_salario(salario, idsalario):
    obj = Salario.objects.get(idSalario=idsalario)
    obj.Salario = salario["salario"]
    obj.ValeTransporte = salario["transporte"]
    # obj.idSalario = obj.Salario
    # obj.idPessoal = obj.idPessoal
    obj.save(update_fields=["Salario", "ValeTransporte"])


def salva_ferias_aquisitivo_inicial(colaborador):
    obj = Ferias()
    obj.DataInicial = colaborador.data_admissao


def create_data_form_periodo_ferias(request, contexto):
    data = dict()
    html_form_periodo_ferias(request, contexto, data)
    return JsonResponse(data)


def html_form_periodo_ferias(request, contexto, data):
    data["html_form_periodo_ferias"] = render_to_string(
        "pessoas/html_form_periodo_ferias.html", contexto, request=request
    )
    return data


# TODO Fazer uma validação conforme data de admissao e pagamentos de salarios
def valida_periodo_ferias(request):
    msg = dict()
    error = False
    hoje = datetime.datetime.today()
    data_inicio = datetime.datetime.strptime(request.POST.get("inicio"), "%Y-%m-%d")
    data_termino = datetime.datetime.strptime(request.POST.get("termino"), "%Y-%m-%d")
    dias = (data_termino - data_inicio).days + 1
    if dias < 5:
        msg["erro_termino"] = "O Período não pode ser menor que 5 dias."
        error = True
    if dias > 30:
        msg["erro_termino"] = "O Período não pode ser maior que 30 dias."
        error = True
    return error, msg


def read_periodo_ferias_post(request):
    periodo_ferias_post = dict()
    periodo_ferias_post["inicio"] = request.POST.get("inicio")
    periodo_ferias_post["termino"] = request.POST.get("termino")
    periodo_ferias_post["idpessoal"] = request.POST.get("idpessoal")
    return periodo_ferias_post


def salva_periodo_ferias_colaborador(idpessoal, inicio, termino, idaquisitivo):
    print(len(connection.queries))
    inicio = datetime.datetime.strptime(inicio, "%Y-%m-%d")
    termino = datetime.datetime.strptime(termino, "%Y-%m-%d")
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    admissao = colaborador.DataAdmissao
    demissao = colaborador.DataDemissao
    valores_colaborador = Salario.objects.get(idPessoal=idpessoal)
    var = dict()
    var["conducao"] = valores_colaborador.ValeTransporte
    mes_inicio = inicio.month
    mes_termino = termino.month
    if mes_inicio == 12:
        mes_termino += 12
    mes_ano = datetime.datetime.strftime(inicio, "%B/%Y")
    mes, ano = converter_mes_ano(mes_ano)
    pdm, udm = extremos_mes(mes, ano)
    cp = CartaoPonto.objects.filter(Dia__range=[pdm, udm], idPessoal=idpessoal)
    if not cp:
        facade_pagamentos.create_cartao_ponto(
            idpessoal, pdm, udm, admissao, demissao, var
        )
    if mes_termino > mes_inicio:
        nova_data = inicio + relativedelta(months=+1)
        mes_ano = datetime.datetime.strftime(nova_data, "%B/%Y")
        mes, ano = converter_mes_ano(mes_ano)
        pdm, udm = extremos_mes(mes, ano)
        cp = CartaoPonto.objects.filter(Dia__range=[pdm, udm], idPessoal=idpessoal)
        if not cp:
            facade_pagamentos.create_cartao_ponto(
                idpessoal, pdm, udm, admissao, demissao, var
            )
        if mes_termino == mes_inicio + 2:
            nova_data = nova_data + relativedelta(months=+1)
            mes_ano = datetime.datetime.strftime(nova_data, "%B/%Y")
            mes, ano = converter_mes_ano(mes_ano)
            pdm, udm = extremos_mes(mes, ano)
            cp = CartaoPonto.objects.filter(Dia__range=[pdm, udm], idPessoal=idpessoal)
            if not cp:
                facade_pagamentos.create_cartao_ponto(
                    idpessoal, pdm, udm, admissao, demissao, var
                )
    print(len(connection.queries))
    CartaoPonto.objects.filter(
        Dia__range=[inicio, termino], idPessoal=idpessoal
    ).update(Ausencia="FÉRIAS", Conducao=0, Remunerado=0, CarroEmpresa=0)
    print(len(connection.queries))
    obj = Ferias()
    print(len(connection.queries))
    obj.DataInicial = inicio
    obj.DataFinal = termino
    obj.idPessoal_id = idpessoal
    obj.idAquisitivo_id = idaquisitivo
    obj.save()
    print(len(connection.queries))


def create_contexto_print_ferias(idpes, idaquisitivo, idparcela):
    colaborador = Colaborador(idpes).__dict__
    aquisitivo = Aquisitivo.objects.get(idAquisitivo=idaquisitivo)
    contexto = {
        "colaborador": colaborador,
        "aquisitivo": aquisitivo,
        "idparcela": idparcela,
    }
    return contexto


def create_data_form_altera_demissao(request, contexto):
    data = dict()
    html_form_altera_demissao(request, contexto, data)
    return JsonResponse(data)


def html_form_altera_demissao(request, contexto, data):
    data["html_form_demissao_colaborador"] = render_to_string(
        "pessoas/html_form_demissao_colaborador.html", contexto, request=request
    )
    return data


# TODO Fazer uma validação conforme data de admissao e pagamentos de salarios
def valida_demissao_colaborador(request):
    msg = dict()
    error = False
    hoje = datetime.datetime.today()
    data_demissao = datetime.datetime.strptime(request.POST.get("demissao"), "%Y-%m-%d")
    if data_demissao > hoje:
        msg["erro_demissao"] = "Você não pode utilizar uma data futura."
        error = True
    return error, msg


def read_demissao_post(request):
    demissao_post = dict()
    demissao_post["demissao"] = datetime.datetime.strptime(
        request.POST.get("demissao"), "%Y-%m-%d"
    )
    demissao_post["idpessoal"] = request.POST.get("idpessoal")
    return demissao_post


def read_demissao_database(idpessoal):
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    demissao_database = dict()
    demissao_database["demissao"] = colaborador.DataDemissao
    demissao_database["idpessoal"] = colaborador.idPessoal
    return demissao_database


def salva_demissao(idpessoal, demissao):
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    aquisitivo = (
        Aquisitivo.objects.filter(idPessoal=idpessoal).order_by("-DataInicial").first()
    )
    obj = Pessoal(colaborador)
    obj.idPessoal = idpessoal
    obj.DataDemissao = demissao
    obj.save(update_fields=["DataDemissao"])
    obj = Aquisitivo(aquisitivo)
    obj.idAquisitivo = aquisitivo.idAquisitivo
    obj.DataFinal = demissao
    obj.save(update_fields=["DataFinal"])


def altera_status(idpessoal):
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    if colaborador.StatusPessoal:
        colaborador.StatusPessoal = False
    else:
        colaborador.StatusPessoal = True
    colaborador.save()
