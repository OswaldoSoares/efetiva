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
