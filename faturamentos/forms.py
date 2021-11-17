from django import forms
from .models import Fatura


class PagaFatura(forms.ModelForm):
    class Meta:
        model = Fatura
        fields = {'idFatura', 'Fatura', 'ValorPagamento', 'DataPagamento', 'StatusFatura'}
        labels = {'ValorPagamento': 'Valor Pago', 'DataPagamento': 'Data Pagamento'}
        widgets = {'ValorPagamento': forms.NumberInput(attrs={'class': 'formfields'}), 'DataPagamento':
                   forms.DateInput(attrs={'class': 'formfields'}), 'Fatura': forms.HiddenInput(), 'StatusFatura':
                   forms.HiddenInput()}
