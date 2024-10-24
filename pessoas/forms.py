import datetime

from django import forms
from .models import (
    Pessoal,
    DocPessoal,
    FonePessoal,
    ContaPessoal,
    Salario,
    Vales,
    ContraCheque,
    ContraChequeItens,
)

MESREFERENCIA = [
    ("1", "JANEIRO"),
    ("2", "FEVEREIRO"),
    ("3", "MARÇO"),
    ("4", "ABRIL"),
    ("5", "MAIO"),
    ("6", "JUNHO"),
    ("7", "JULHO"),
    ("8", "AGOSTO"),
    ("9", "SETEMBRO"),
    ("10", "OUTUBRO"),
    ("11", "NOVEMBRO"),
    ("12", "DEZEMBRO"),
]

hoje = datetime.date.today()
ANOREFERENCIA = [
    (hoje.year - 1, hoje.year - 1),
    (hoje.year, hoje.year),
    (hoje.year + 1, hoje.year + 1),
]


class MeuDateInput(forms.DateInput):
    input_type = "date"


class CadastraSalario(forms.ModelForm):
    class Meta:
        model = Salario
        fields = ("idPessoal", "Salario", "HorasMensais", "ValeTransporte")
        labels = {
            "Salario": "formfields",
            "HorasMensais": "HORAS MENSAIS",
            "ValeTransporte": "VALE TRANSPORTE",
        }
        widgets = {
            "Salario": forms.NumberInput(attrs={"class": "form-control"}),
            "idPessoal": forms.HiddenInput(),
            "HorasMensais": forms.NumberInput(attrs={"class": "form-control"}),
            "ValeTransporte": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
        }


class CadastraVale(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraVale, self).__init__(*args, **kwargs)
        self.fields["Data"].initial = datetime.date.today()

    class Meta:
        model = Vales
        fields = ("idPessoal", "Data", "Descricao", "Valor")
        labels = {
            "Data": "DATA",
            "Descricao": "DESCRIÇÃo",
            "Valor": "VALOR",
            "idPessoal": "COLABORADOR",
        }
        widgets = {
            "Data": MeuDateInput(
                format="%Y-%m-%d", attrs={"class": "form-control"}
            ),
            "Descricao": forms.TextInput(attrs={"class": "form-control"}),
            "Valor": forms.NumberInput(attrs={"class": "form-control"}),
            "idPessoal": forms.Select(attrs={"class": "form-control"}),
        }


class CadastraContraCheque(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraContraCheque, self).__init__(*args, **kwargs)
        self.fields["MesReferencia"].initial = hoje.month
        self.fields["AnoReferencia"].initial = hoje.year

    class Meta:
        model = ContraCheque
        fields = ("MesReferencia", "AnoReferencia", "Valor", "idPessoal")
        labels = {
            "MesReferencia": "MÊS REFERÊNCIA",
            "AnoReferencia": "ANO REFERÊNCIA",
        }
        widgets = {
            "MesReferencia": forms.Select(
                attrs={"class": "form-control"}, choices=MESREFERENCIA
            ),
            "AnoReferencia": forms.Select(
                attrs={"class": "form-control"}, choices=ANOREFERENCIA
            ),
        }


class CadastraContraChequeItens(forms.ModelForm):
    class Meta:
        model = ContraChequeItens
        fields = ("Descricao", "Valor", "Registro", "idContraCheque")
        lables = {"Descricao": "DESCRIÇÃO", "Valor": "VALOR"}
        widgets = {
            "Descricao": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "DESCRIÇÃO"}
            ),
            "Valor": forms.NumberInput(attrs={"class": "form-control"}),
            "Registro": forms.Select(
                attrs={"class": "form-control"},
                choices=[("C", "CRÉDITO"), ("D", "DÉBITO")],
            ),
        }


class CadastraDemissao(forms.ModelForm):
    class Meta:
        model = Pessoal
        fields = ("DataDemissao",)
        widgets = {
            "DataDemissao": MeuDateInput(
                format="%Y-%m-%d", attrs={"class": "form-control"}
            )
        }


class FormVale(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormVale, self).__init__(*args, **kwargs)
        self.fields["Data"].initial = datetime.date.today()

    class Meta:
        model = Vales
        fields = ("idPessoal", "Data", "Descricao", "Valor")
        widgets = {
            "Data": MeuDateInput(
                format="%Y-%m-%d", attrs={"class": "form-control"}
            ),
            "Descricao": forms.TextInput(attrs={"class": "form-control"}),
            "Valor": forms.NumberInput(attrs={"class": "form-control"}),
            "idPessoal": forms.Select(attrs={"class": "form-control"}),
        }
