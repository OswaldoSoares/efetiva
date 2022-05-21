import datetime
from decimal import Decimal

from django.http import JsonResponse
from django.template.loader import render_to_string
from veiculos.models import Veiculo

from despesas.models import Abastecimento, Multas


def create_despesas_context():
    abastecimento = get_abastecimento_all()
    veiculos = Veiculo.objects.all()
    multas = Multas.objects.filter(Pago=False).order_by("-Vencimento")
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    context = {
        "abastecimento": abastecimento,
        "veiculos": veiculos,
        "hoje": hoje,
        "multas": multas,
    }
    return context


def get_abastecimento_all():
    return Abastecimento.objects.all()


def form_despesa(request, c_form, c_idobj, c_url, c_view):
    data = dict()
    c_instance = None
    form = c_form(instance=c_instance)
    contexto = {"form": form, "c_idobj": c_idobj, "c_url": c_url, "c_view": c_view}
    data["html_html"] = render_to_string(
        "despesas/formdespesa.html", contexto, request=request
    )
    c_return = JsonResponse(data)
    return c_return


def valida_multa(request, _var):
    msg = dict()
    data = dict()
    error = False
    # Valida Número AIT
    _ait = request.POST.get("ait")
    if not _ait:
        msg["erro_ait"] = "Obrigatório o número AIT."
        error = True
    # Valida Número DOC
    _doc = request.POST.get("doc")
    if not _doc:
        msg["erro_doc"] = "Obrigatório o número DOC."
        error = True
    # Valida Data da infração
    _data = datetime.datetime.strptime(request.POST.get("data"), "%Y-%m-%d").date()
    _hoje = datetime.datetime.today().date()
    if _data >= _hoje:
        msg["erro_data"] = "Data da infração tem que ser anterior a hoje."
        error = True
    _hora = request.POST.get("hora")
    # Valida infração
    _infracao = request.POST.get("infracao")
    if not _infracao:
        msg["erro_infracao"] = "Obrigatório o tipo de infração."
        error = True
    # Valida local da infração
    _local = request.POST.get("local")
    if not _local:
        msg["erro_local"] = "Obrigatório o local da infração."
        error = True
    # Valida valor da infração
    _valor = request.POST.get("valor")
    if Decimal(_valor) < Decimal("0.01"):
        msg["erro_valor"] = "Obrigatório o valor da multa."
        error = True
    # Valida vencimento da infração
    _vencimento = datetime.datetime.strptime(
        request.POST.get("vencimento"), "%Y-%m-%d"
    ).date()
    if _vencimento == _data:
        msg[
            "erro_vencimento"
        ] = "A data de vencimento não pode ser a mesma da infração."
        error = True
    if _vencimento < _data:
        msg[
            "erro_vencimento"
        ] = "A data de vencimento não pode ser anterior a data da infração."
        error = True
    # Valida veículo da infração
    _veiculo = request.POST.get("veiculo")
    if not _veiculo:
        msg["erro_veiculo"] = "Obrigatório selecionar um veículo."
        error = True
    # Valida quem paga a infração
    _desconta = request.POST.get("desconta")
    if not _desconta:
        msg["erro_desconta"] = "Obrigatório selecionar quem paga a multa."
        error = True
    contexto = create_despesas_context()
    contexto.update(msg)
    data["html_form_multas"] = render_to_string(
        "despesas/html_form_multas.html", contexto, request=request
    )
    if not error:
        save_multa(request)
    return JsonResponse(data)


def save_multa(request):
    obj = Multas()
    obj.NumeroAIT = request.POST.get("ait")
    obj.NumeroDOC = request.POST.get("doc")
    obj.DataMulta = datetime.datetime.strptime(
        request.POST.get("data"), "%Y-%m-%d"
    ).date()
    obj.HoraMulta = datetime.datetime.strptime(request.POST.get("hora"), "%H:%M").time()
    obj.ValorMulta = request.POST.get("valor")
    obj.Vencimento = datetime.datetime.strptime(
        request.POST.get("vencimento"), "%Y-%m-%d"
    ).date()
    obj.DataPagamento = datetime.datetime.strptime(
        request.POST.get("vencimento"), "%Y-%m-%d"
    ).date()
    obj.Infracao = request.POST.get("infracao")
    obj.Local = request.POST.get("local")
    if request.POST.get("desconta"):
        obj.DescontaMotorista = True
    obj.idVeiculo_id = request.POST.get("veiculo")
    obj.save()
