import datetime
from decimal import Decimal

from django import forms

from veiculos.models import Veiculo

from .models import Abastecimento

# Proprietário dos veículos da frota própria
ID_PROPRIETARIO_FROTA = 17

# Diferença máxima aceita entre o valor total e litros x preço do litro
TOLERANCIA_VALOR = Decimal("0.10")


class CadastraAbastecimento(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = [
            "DataAbastecimento",
            "idVeiculo",
            "TipoCombustivel",
            "LitrosAbastecidos",
            "ValorCombustivel",
            "ValorAbastecido",
        ]
        labels = {
            "DataAbastecimento": "DATA",
            "idVeiculo": "VEÍCULO",
            "TipoCombustivel": "COMBUSTÍVEL",
            "LitrosAbastecidos": "LITROS",
            "ValorCombustivel": "PREÇO DO LITRO",
            "ValorAbastecido": "VALOR TOTAL",
        }
        widgets = {
            "DataAbastecimento": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "LitrosAbastecidos": forms.NumberInput(
                attrs={"step": "0.01", "min": "0.01"}
            ),
            "ValorCombustivel": forms.NumberInput(
                attrs={"step": "0.001", "min": "0.001"}
            ),
            "ValorAbastecido": forms.NumberInput(
                attrs={"step": "0.01", "min": "0.01"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idVeiculo"].queryset = Veiculo.objects.filter(
            Proprietario_id=ID_PROPRIETARIO_FROTA
        ).order_by("Placa")
        self.fields["idVeiculo"].label_from_instance = lambda obj: obj.Placa
        if not self.instance.pk and not self.is_bound:
            self.initial.setdefault(
                "DataAbastecimento", datetime.date.today()
            )
        for field in self.fields.values():
            css = "form-select" if field.widget.input_type == "select" else (
                "form-control"
            )
            field.widget.attrs.setdefault("class", css)

    def clean_DataAbastecimento(self):
        data = self.cleaned_data["DataAbastecimento"]
        if data > datetime.date.today():
            raise forms.ValidationError("A data não pode ser futura.")
        return data

    def _clean_positivo(self, campo):
        valor = self.cleaned_data[campo]
        if valor <= 0:
            raise forms.ValidationError("Informe um valor maior que zero.")
        return valor

    def clean_LitrosAbastecidos(self):
        return self._clean_positivo("LitrosAbastecidos")

    def clean_ValorCombustivel(self):
        return self._clean_positivo("ValorCombustivel")

    def clean_ValorAbastecido(self):
        return self._clean_positivo("ValorAbastecido")

    def clean(self):
        cleaned_data = super().clean()
        litros = cleaned_data.get("LitrosAbastecidos")
        preco = cleaned_data.get("ValorCombustivel")
        total = cleaned_data.get("ValorAbastecido")
        if litros and preco and total:
            calculado = (litros * preco).quantize(Decimal("0.01"))
            if abs(calculado - total) > TOLERANCIA_VALOR:
                self.add_error(
                    "ValorAbastecido",
                    f"Valor não confere com litros x preço "
                    f"(R$ {calculado}).",
                )
        return cleaned_data
