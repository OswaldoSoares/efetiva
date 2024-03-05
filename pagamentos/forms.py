from django import forms

from pessoas.models import CartaoPonto, Agenda
import datetime

hoje = datetime.date.today()


class MeuTimeInput(forms.TimeInput):
    input_type = "time"


class MeuDateInput(forms.DateInput):
    input_type = "date"


class CadastraCartaoPonto(forms.ModelForm):
    class Meta:
        model = CartaoPonto
        fields = "__all__"
        labels = {"Entrada": "HORA ENTRADA", "Saida": "HORA SAIDA"}
        widgets = {
            "Entrada": MeuTimeInput(
                attrs={"class": "form-control", "pattern": "[0-9]{2}:[0-9]{2}"}
            ),
            "Saida": MeuTimeInput(
                attrs={"class": "form-control", "pattern": "[0-9]{2}:[0-9]{2}"}
            ),
        }


class FormAgenda(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAgenda, self).__init__(*args, **kwargs)
        self.fields["Dia"].initial = datetime.date.today()

    class Meta:
        model = Agenda
        fields = ("Dia", "Descricao")
        widgets = {
            "Dia": MeuDateInput(
                format="%Y-%m-%d", attrs={"class": "form-control"}
            ),
            "Descricao": forms.Textarea(attrs={"class": "form-control"}),
        }
