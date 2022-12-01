import calendar
import datetime
import os
from django.db import connection

from django.db.models import Sum
from django.http import JsonResponse
from django.template.loader import render_to_string
from decimal import Decimal

from pessoas.forms import CadastraSalario, CadastraVale, CadastraDemissao
from pessoas.models import (
    DecimoTerceiro,
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
from website.facade import nome_curto

from transefetiva.settings.development import MEDIA_ROOT

# from transefetiva.settings.production import MEDIA_ROOT

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
        self.data_demissao = colaborador.DataDemissao
        self.foto = colaborador.Foto
        self.documentos = ColaboradorDocumentos(idpes).docs
        self.telefones = ColaboradorTelefones(idpes).fone
        self.bancos = ColaboradorBancos(idpes).conta
        self.decimo_terceiro = self.get_decimo_terceiro(self)

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
        return lista


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


def altera_status(idpessoal):
    pessoa = Pessoal.objects.get(idPessoal=idpessoal)
    if pessoa.StatusPessoal:
        pessoa.StatusPessoal = False
    else:
        pessoa.StatusPessoal = True
    pessoa.save()


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
def create_contexto_colaboradores_ativo():
    colaboradores = Pessoal.objects.filter(StatusPessoal=True)
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


def create_contexto_consulta_colaborador(idpessoal):
    colaborador = Colaborador(idpessoal).__dict__
    return {"colaborador": colaborador}


def create_data_consulta_colaborador(request, contexto):
    data = dict()
    html_dados_colaborador(request, contexto, data)
    html_decimo_terceiro(request, contexto, data)
    return JsonResponse(data)


def html_dados_colaborador(request, contexto, data):
    data["html_dados_colaborador"] = render_to_string(
        "pessoas/html_dados_colaborador.html", contexto, request=request
    )
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
    if documento == None:
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
    return {"mensagem": mensagem, "iddocpessoal": iddocpessoal, "idpessoal": idpessoal}


def apaga_documento(iddocpessoal):
    documento = DocPessoal.objects.get(idDocPessoal=iddocpessoal)
    documento.delete()


def create_data_form_adiciona_fone_colaborador(request, contexto):
    data = dict()
    html_form_adiciona_fone_colaborador(request, contexto, data)
    return JsonResponse(data)
