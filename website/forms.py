from django import forms
from .models import Parametros


PARAMETROS_CHAVE = [
    ('TABELA PADRAO', 'TABELA PADRÃO')
]


class CadastraParametro(forms.ModelForm):
    class Meta:
        models = Parametros
        fields = ['Chave', 'Valor']
        widgets = {'Chave': forms.Select(attrs={'class': 'form-control'}),
                   'Valor': forms.TextInput(attrs={'class': 'form-control'})}
