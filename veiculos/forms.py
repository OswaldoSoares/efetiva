import re
from decimal import Decimal

from django import forms
from django.db.models import Q

from pessoas.models import Pessoal

from .models import CategoriaVeiculo, Veiculo

# Placa antiga (ABC1234) ou Mercosul (ABC1D23), sem espaço ou hífen
PADRAO_PLACA = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")

CAMPOS_MEDIDA = (
    "Capacidade",
    "MedidaAltura",
    "MedidaComprimento",
    "MedidaLargura",
)


def normalizar_placa(placa):
    return re.sub(r"[^A-Z0-9]", "", (placa or "").upper())


class CadastraVeiculo(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = (
            "Placa",
            "Categoria",
            "Marca",
            "Modelo",
            "Ano",
            "Cor",
            "Combustivel",
            "Renavam",
            "RNTRC",
            "Rastreador",
            "Proprietario",
            "Motorista",
            "Capacidade",
            "MedidaAltura",
            "MedidaComprimento",
            "MedidaLargura",
        )
        labels = {
            "Placa": "PLACA",
            "Categoria": "CATEGORIA",
            "Marca": "MARCA",
            "Modelo": "MODELO",
            "Ano": "ANO",
            "Cor": "COR",
            "Combustivel": "COMBUSTÍVEL",
            "Renavam": "RENAVAM",
            "RNTRC": "RNTRC",
            "Rastreador": "RASTREADOR",
            "Proprietario": "PROPRIETÁRIO",
            "Motorista": "MOTORISTA",
            "Capacidade": "CAPACIDADE (KG)",
            "MedidaAltura": "ALTURA (M)",
            "MedidaComprimento": "COMPRIMENTO (M)",
            "MedidaLargura": "LARGURA (M)",
        }
        widgets = {
            "Placa": forms.TextInput(
                attrs={"placeholder": "ABC1D23", "autocomplete": "off"}
            ),
            "Ano": forms.TextInput(attrs={"inputmode": "numeric"}),
            "Renavam": forms.TextInput(attrs={"inputmode": "numeric"}),
            # inputmode="decimal": teclado numérico com vírgula no celular
            "Capacidade": forms.NumberInput(
                attrs={"step": "0.01", "min": "0", "inputmode": "decimal"}
            ),
            "MedidaAltura": forms.NumberInput(
                attrs={"step": "0.01", "min": "0", "inputmode": "decimal"}
            ),
            "MedidaComprimento": forms.NumberInput(
                attrs={"step": "0.01", "min": "0", "inputmode": "decimal"}
            ),
            "MedidaLargura": forms.NumberInput(
                attrs={"step": "0.01", "min": "0", "inputmode": "decimal"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Só pessoas ativas; na edição mantém quem já está gravado
        for campo in ("Proprietario", "Motorista"):
            filtro = Q(StatusPessoal=True)
            atual = getattr(self.instance, f"{campo}_id", None)
            if atual:
                filtro |= Q(pk=atual)
            self.fields[campo].queryset = Pessoal.objects.filter(
                filtro
            ).order_by("Nome")
        self.fields["Categoria"].queryset = CategoriaVeiculo.objects.order_by(
            "Categoria"
        )
        for campo in ("Categoria", "Proprietario", "Motorista"):
            self.fields[campo].empty_label = "Selecione..."
        for campo in CAMPOS_MEDIDA:
            self.fields[campo].required = False
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_Placa(self):
        placa = normalizar_placa(self.cleaned_data["Placa"])
        if not PADRAO_PLACA.match(placa):
            raise forms.ValidationError(
                "Placa inválida. Use o formato ABC1234 ou ABC1D23."
            )
        outros = Veiculo.objects.exclude(pk=self.instance.pk)
        # Placas antigas podem estar gravadas com espaço ou hífen
        if any(
            normalizar_placa(p) == placa
            for p in outros.values_list("Placa", flat=True)
        ):
            raise forms.ValidationError("Já existe um veículo com esta placa.")
        return placa

    def clean_Combustivel(self):
        return self.cleaned_data["Combustivel"].strip().upper()

    def clean(self):
        cleaned_data = super().clean()
        # As colunas não aceitam nulo: campo vazio é gravado como zero
        for campo in CAMPOS_MEDIDA:
            if cleaned_data.get(campo) is None and campo not in self.errors:
                cleaned_data[campo] = Decimal("0")
        return cleaned_data


class CadastraCategoria(forms.ModelForm):
    class Meta:
        model = CategoriaVeiculo
        fields = ("Categoria",)
        labels = {"Categoria": "CATEGORIA"}
        widgets = {
            "Categoria": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "off"}
            ),
        }

    def clean_Categoria(self):
        categoria = " ".join(self.cleaned_data["Categoria"].split()).upper()
        existe = CategoriaVeiculo.objects.filter(
            Categoria__iexact=categoria
        ).exclude(pk=self.instance.pk)
        if existe.exists():
            raise forms.ValidationError("Esta categoria já existe.")
        return categoria
