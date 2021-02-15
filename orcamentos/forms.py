import datetime

from django import forms
from .models import Orcamento


class MeuDateInput(forms.DateInput):
    input_type = 'date'


class CadastraOrcamento(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraOrcamento, self).__init__(*args, **kwargs)
        self.fields['DataOrcamento'].initial = datetime.date.today()
        self.fields['idCategoriaVeiculo'].empty_label = 'SELECIONE UM ITEM'

    class Meta:
        model = Orcamento
        fields = ['DataOrcamento', 'Solicitante', 'Contato', 'Email', 'Telefone', 'Destino', 'KM', 'Perimetro',
                  'Pedagio', 'Despesas', 'ValorTabela', 'QuantidadeAjudantes', 'Ajudantes', 'TaxaExpedicao',
                  'StatusOrcamento', 'Comentario', 'idCategoriaVeiculo', 'Valor']
        labels = []
        widgets = {'DataOrcamento': MeuDateInput(format='%Y-%m-%d', attrs={'class': 'form-control'}),
                   'Solicitante': forms.TextInput(attrs={'class': 'form-control'}),
                   'Contato': forms.TextInput(attrs={'class': 'form-control'}),
                   'Email': forms.EmailInput(attrs={'class': 'form-control'}),
                   'Telefone': forms.TextInput(attrs={'class': 'form-control'}),
                   'idCategoriaVeiculo': forms.Select(attrs={'class': 'form-control'}),
                   'Destino': forms.TextInput(attrs={'class': 'form-control'}),
                   'ValorTabela': forms.NumberInput(attrs={'class': 'form-control'}),
                   'KM': forms.NumberInput(attrs={'class': 'form-control'}),
                   'Perimetro': forms.NumberInput(attrs={'class': 'form-control'}),
                   'Pedagio': forms.NumberInput(attrs={'class': 'form-control'}),
                   'Despesas': forms.NumberInput(attrs={'class': 'form-control'}),
                   'QuantidadeAjudantes': forms.NumberInput(attrs={'class': 'form-control'}),
                   'Ajudantes': forms.NumberInput(attrs={'class': 'form-control'}),
                   'TaxaExpedicao': forms.NumberInput(attrs={'class': 'form-control'}),
                   'Comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
                   'Valor': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'True'}),
                   'StatusOrcamento': forms.HiddenInput()}
