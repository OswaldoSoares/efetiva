from django import forms
from .models import Abastecimento


class CadastraAbastecimento(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = {'idAbastecimento', 'DataAbastecimento', 'LitrosAbastecidos', 'ValorAbastecido', 'ValorCombustivel',
                  'TipoCombustivel', 'idVeiculo'}
