from django import forms
from django.core.exceptions import ValidationError

from .models import (
    Cliente,
    FoneContatoCliente,
    EMailContatoCliente,
    Cobranca,
    Tabela,
    TabelaVeiculo,
    TabelaCapacidade,
    TabelaPerimetro,
    FormaPagamento,
)

TIPOFONE = [
    ("WHATSAPP", "WHATSAPP"),
    ("VIVO", "VIVO"),
    ("TIM", "TIM"),
    ("OI", "OI"),
    ("NEXTEL", "NEXTEL"),
    ("CLARO", "CLARO"),
    ("FIXO", "FIXO"),
    ("RECADO", "RECADO"),
]


class MeuTimeInput(forms.TimeInput):
    input_type = "time"


class CadastraCliente(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"
        labels = {
            "Fantasia": "NOME FANTASIA",
            "Nome": "RAZÃO SOCIAL",
            "Endereco": "ENDEREÇO",
            "Bairro": "BAIRRO",
            "CEP": "CEP",
            "Cidade": "CIDADE",
            "Estado": "ESTADO",
            "CNPJ": "CNPJ",
            "IE": "INSCRIÇÃO ESTADUAL",
            "Site": "SITE",
        }
        widgets = {
            "Fantasia": forms.TextInput(),
            "Nome": forms.TextInput(),
            "Endereco": forms.TextInput(),
            "Bairro": forms.TextInput(),
            "CEP": forms.TextInput(),
            "CNPJ": forms.TextInput(),
            "IE": forms.TextInput(),
            "Cidade": forms.TextInput(attrs={"value": "São  Paulo"}),
            "Estado": forms.TextInput(attrs={"value": "SP"}),
            "Site": forms.TextInput(),
        }

    def clean_fantasia(self):
        fantasia = self.cleaned_data["Fantasia"]
        if Cliente.objects.filter(Fantasia=fantasia).exists():
            if not self.instance.idCliente:
                raise ValidationError("Cliente com este Fantasia já existe.")
        return fantasia


class CadastraFoneContatoCliente(forms.ModelForm):
    class Meta:
        model = FoneContatoCliente
        fields = ("Contato", "TipoFone", "Fone", "idCliente")
        labels = {
            "Contato": "CONTATO",
            "TipoFone": "OPERADORA",
            "Fone": "TELEFONE",
        }
        widgets = {
            "Contato": forms.TextInput(),
            "TipoFone": forms.Select(),
            "Fone": forms.TextInput(),
            "idCliente": forms.HiddenInput(),
        }


class CadastraEMailContatoCliente(forms.ModelForm):
    class Meta:
        model = EMailContatoCliente
        fields = ("Contato", "EMail", "RecebeFatura", "idCliente")
        labels = {
            "Contato": "CONTATO",
            "EMail": "E-MAIL",
            "RcebeFatura": "RECEBE FATURA",
        }
        widgets = {
            "Contato": forms.TextInput(),
            "EMail": forms.EmailInput(),
            "RecebeFatura": forms.CheckboxInput(),
            "idCliente": forms.HiddenInput(),
        }


class CadastraCobranca(forms.ModelForm):
    class Meta:
        model = Cobranca
        fields = (
            "Nome",
            "Endereco",
            "Bairro",
            "CEP",
            "Cidade",
            "Estado",
            "CNPJ",
            "IE",
            "idCliente",
        )
        labels = {
            "Nome": "RAZÃO SOCIAL",
            "Endereco": "ENDEREÇO",
            "Bairro": "BAIRRO",
            "CEP": "CEP",
            "Cidade": "CIDADE",
            "Estado": "ESTADO",
            "CNPJ": "CNPJ",
            "IE": "INSCRIÇÃO ESTADUAL",
        }
        widgets = {
            "Nome": forms.TextInput(),
            "Endereco": forms.TextInput(),
            "Bairro": forms.TextInput(),
            "CEP": forms.TextInput(),
            "Cidade": forms.TextInput(),
            "Estado": forms.TextInput(),
            "CNPJ": forms.TextInput(),
            "IE": forms.TextInput(),
            "idCliente": forms.HiddenInput(),
        }


class CadastraTabela(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraTabela, self).__init__(*args, **kwargs)
        # Personaliza opcão o do SELECT
        self.fields[
            "idFormaPagamento"
        ].empty_label = "SELECIONE UM ITEM DA LISTA"

    class Meta:
        model = Tabela
        fields = (
            "Comissao",
            "Seguro",
            "TaxaExpedicao",
            "AjudanteCobra",
            "AjudanteCobraHoraExtra",
            "AjudantePaga",
            "idFormaPagamento",
            "idCliente",
        )
        labels = {
            "Comissao": "PORCENTAGEM DA COMISSÃO",
            "Seguro": "PORCENTAGEM DO SEGURO",
            "TaxaExpedicao": "TAXA EXPEDIÇÃO",
            "AjudanteCobra": "VALOR AJUDANTE À RECEBER",
            "AjudanteCobraHoraExtra": "VALOR AJUDANTE À RECEBER HORA EXTRA",
            "AjudantePaga": "VALOR AJUDANTE À PAGAR",
            "idFormaPagamento": "FORMA DE PAGAMENTO",
        }
        widgets = {
            "Comissao": forms.NumberInput(attrs={"class": "form-control"}),
            "Seguro": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.001"}
            ),
            "TaxaExpedicao": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "AjudanteCobra": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "AjudanteCobraHoraExtra": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "AjudantePaga": forms.NumberInput(attrs={"class": "form-control"}),
            "idFormaPagamento": forms.Select(attrs={"class": "form-control"}),
            "idCliente": forms.HiddenInput(),
        }


class CadastraTabelaVeiculo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraTabelaVeiculo, self).__init__(*args, **kwargs)
        self.fields["HoraMinimo"].initial = "00:00"

    class Meta:
        model = TabelaVeiculo
        fields = (
            "PorcentagemCobra",
            "PorcentagemPaga",
            "HoraCobra",
            "HoraPaga",
            "HoraMinimo",
            "KMCobra",
            "KMPaga",
            "KMMinimo",
            "EntregaCobra",
            "EntregaPaga",
            "EntregaMinimo",
            "EntregaKGCobra",
            "EntregaKGPaga",
            "EntregaVolumeCobra",
            "EntregaVolumePaga",
            "SaidaCobra",
            "SaidaPaga",
            "idCliente",
            "idCategoriaVeiculo",
        )
        labels = {
            "PorcentagemCobra": "PORCENTAGEM DAS NOTAS À RECEBER",
            "PorcentagemPaga": "PORCENTAGEM DAS NOTAS À PAGAR",
            "HoraCobra": "VALOR DA HORA À RECEBER",
            "HoraPaga": "VALOR DA HORA À PAGAR",
            "HoraMinimo": "MÍNIMO DE HORAS",
            "KMCobra": "VALOR DO KILOMETRO À RECEBER",
            "KMPaga": "VALOR DO KILOMETRO À PAGAR",
            "KMMinimo": "MÍNIMO DE KILOMETROS",
            "EntregaCobra": "VALOR DA ENTREGA À RECEBER",
            "EntregaPaga": "VALOR DA ENTREGA À PAGAR",
            "EntregaMinimo": "MÍNIMO DE ENTREGAS",
            "EntregaKGCobra": "VALOR KG À RECEBER",
            "EntregaKGPaga": "VALOR KG À PAGAR",
            "EntregaVolumeCobra": "VALOR VOLUME À RECEBER",
            "EntregaVolumePaga": "VALOR VOLUME À PAGAR",
            "SaidaCobra": "VALOR DA SAÍDA À RECEBER",
            "SaidaPaga": "VALOR DA SAÍDA À PAGAR",
        }
        widgets = {
            "PorcentagemCobra": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "PorcentagemPaga": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "HoraCobra": forms.NumberInput(attrs={"class": "form-control"}),
            "HoraPaga": forms.NumberInput(attrs={"class": "form-control"}),
            "HoraMinimo": MeuTimeInput(
                attrs={"class": "form-control", "pattern": "[0-9]{2}:[0-9]{2}"}
            ),
            "KMCobra": forms.NumberInput(attrs={"class": "form-control"}),
            "KMPaga": forms.NumberInput(attrs={"class": "form-control"}),
            "KMMinimo": forms.NumberInput(attrs={"class": "form-control"}),
            "EntregaCobra": forms.NumberInput(attrs={"class": "form-control"}),
            "EntregaPaga": forms.NumberInput(attrs={"class": "form-control"}),
            "EntregaMinimo": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "EntregaKGCobra": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "EntregaKGPaga": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "EntregaVolumeCobra": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "EntregaVolumePaga": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "SaidaCobra": forms.NumberInput(attrs={"class": "form-control"}),
            "SaidaPaga": forms.NumberInput(attrs={"class": "form-control"}),
            "idCliente": forms.HiddenInput(attrs={}),
            "idCategoriaVeiculo": forms.HiddenInput(attrs={}),
        }


class CadastraTabelaCapacidade(forms.ModelForm):
    class Meta:
        model = TabelaCapacidade
        fields = (
            "CapacidadeInicial",
            "CapacidadeFinal",
            "CapacidadeCobra",
            "CapacidadePaga",
            "idCliente",
        )
        labels = {
            "CapacidadeInicial": "CAPACIDADE (KGs) INICIAL",
            "CapacidadeFinal": "CAPACIDADE (KGs) FINAL",
            "CapacidadeCobra": "CAPACIDADE COBRA",
            "CapacidadePaga": "CAPACIDADE PAGA",
        }
        widgets = {
            "CapacidadeInicial": forms.NumberInput(
                attrs={"class": "form-control", "readonly": True}
            ),
            "CapacidadeFinal": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "CapacidadeCobra": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "CapacidadePaga": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "idCliente": forms.HiddenInput(),
        }


class CadastraTabelaPerimetro(forms.ModelForm):
    class Meta:
        model = TabelaPerimetro
        fields = (
            "PerimetroInicial",
            "PerimetroFinal",
            "PerimetroCobra",
            "PerimetroPaga",
            "idCliente",
        )
        labels = {
            "PerimetroInicial": "PERIMETRO (KMs) INICIAL",
            "PerimetroFinal": "PERIMETRO (KMs) FINAL",
            "PerimetroCobra": "PERIMETRO COBRA",
            "PerimetroPaga": "PERIMETRO PAGA",
        }
        widgets = {
            "PerimetroInicial": forms.NumberInput(
                attrs={"class": "form-control", "readonly": True}
            ),
            "PerimetroFinal": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "PerimetroCobra": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "PerimetroPaga": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "idCliente": forms.HiddenInput(),
        }


class CadastraFormaPgto(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = {"Forma", "Dias"}
        labels = {"Forma": "FORMA", "Dias": "DIAS"}
        widgets = {
            "Forma": forms.TextInput(
                attrs={
                    "class": "formfields",
                    # 'placeholder': 'PERÍODO PARA FATURAR ',
                }
            ),
            "Dias": forms.NumberInput(
                attrs={
                    "class": "formfields",
                    # 'placeholder': 'DIAS PARA PAGAR'
                }
            ),
        }
