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
            "ValorAbastecido",
            "ValorCombustivel",
            "LitrosAbastecidos",
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
            # Texto com máscara: no type="date" o Tab percorre dia/mês/ano
            "DataAbastecimento": forms.DateInput(
                attrs={
                    "class": "form-control js-abastecimento-data",
                    "placeholder": "dd/mm/aaaa",
                    "inputmode": "numeric",
                    "autocomplete": "off",
                },
                format="%d/%m/%Y",
            ),
            # inputmode="decimal": teclado numérico com vírgula no celular
            "LitrosAbastecidos": forms.NumberInput(
                attrs={"step": "0.01", "min": "0.01", "inputmode": "decimal"}
            ),
            "ValorCombustivel": forms.NumberInput(
                attrs={"step": "0.001", "min": "0.001", "inputmode": "decimal"}
            ),
            "ValorAbastecido": forms.NumberInput(
                attrs={"step": "0.01", "min": "0.01", "inputmode": "decimal"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idVeiculo"].queryset = Veiculo.objects.filter(
            Proprietario_id=ID_PROPRIETARIO_FROTA
        ).order_by("Placa")
        self.fields["idVeiculo"].label_from_instance = lambda obj: obj.Placa
        self.fields["DataAbastecimento"].input_formats = [
            "%d/%m/%Y",
            "%Y-%m-%d",
        ]
        if not self.instance.pk and not self.is_bound:
            self.initial.setdefault(
                "DataAbastecimento", datetime.date.today()
            )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

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
                litros_esperados = (total / preco).quantize(Decimal("0.01"))
                self.add_error(
                    "LitrosAbastecidos",
                    f"Litros não conferem com valor ÷ preço "
                    f"({litros_esperados} L).",
                )
        return cleaned_data
