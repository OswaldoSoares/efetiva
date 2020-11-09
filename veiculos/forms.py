from django import forms
from .models import Veiculo, CategoriaVeiculo

class CadastraVeiculo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraVeiculo, self).__init__(*args, **kwargs)

    Cubagem = forms.DecimalField(label='CUBAGEM', widget=forms.NumberInput(attrs={'class': 'formfields', 'readonly': 'True'}))
    class Meta:
        model = Veiculo
        fields = (
            'Marca',
            'Modelo',
            'Placa',
            'Cor',
            'Ano',
            'Renavam',
            'Combustivel',
            'Rastreador',
            'RNTRC',
            'Capacidade',
            'MedidaAltura',
            'MedidaComprimento',
            'MedidaLargura',
            'Cubagem',
            'Proprietario',
            'Motorista',
            'Categoria',
        )
        labels = {
            'Marca': 'MARCA',
            'Modelo': 'MODELO',
            'Placa': 'PLACA',
            'Cor': 'COR',
            'Ano': 'ANO',
            'Renavam': 'RENAVAM',
            'Combustivel': 'COMBUSTÍVEL',
            'Rastreador': 'RASTREADOR',
            'RNTRC': 'RNTRC',
            'Capacidade': 'CAPACIDADE',
            'MedidaAltura': 'ALTURA',
            'MedidaComprimento': 'COMPRIMENTO',
            'MedidaLargura': 'LARGURA',
            'Proprietario': 'PROPRIETÁRIO',
            'Motorista': 'MOTORISTA',
            'Categoria': 'CATEGORIA',
        }
        widgets = {
            'Marca': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Modelo': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Placa': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Cor': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Ano': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Renavam': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Combustivel': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Rastreador': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'RNTRC': forms.TextInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Capacidade': forms.NumberInput(
                attrs={
                    'class': 'formfields'
                }
            ),
            'MedidaAltura': forms.NumberInput(
                attrs={
                    'class': 'formfields teste'
                }
            ),
            'MedidaComprimento': forms.NumberInput(
                attrs={
                    'class': 'formfields teste'
                }
            ),
            'MedidaLargura': forms.NumberInput(
                attrs={
                    'class': 'formfields teste'
                }
            ),
            'Proprietario': forms.Select(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Motorista': forms.Select(
                attrs={
                    'class': 'formfields'
                }
            ),
            'Categoria': forms.Select(
                attrs={
                    'class': 'formfields'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(CadastraVeiculo, self).__init__(*args, **kwargs)
        self.fields['Motorista'].empty_label = 'Selecione um item da lista...'
        self.fields['Proprietario'].empty_label = 'Selecione um item da lista...'
        self.fields['Categoria'].empty_label = 'Selecione um item da lista...'


class CadastraCategoria(forms.ModelForm):
    class Meta:
        model = CategoriaVeiculo
        fields = ('Categoria',)
        widgets = {
            'Categoria': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    'placeholder': 'Categoria:'
                }
            ),
        }
