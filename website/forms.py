from django import forms
from .models import Parametros
from clientes.facade import create_select_cliente
from website.models import FileUpload


parametros_chave = [
    ('', ''),
    ('TABELA PADRAO', 'TABELA PADRÃO'),
    ('DESPESA', 'DESPESA')
]


fantasia = create_select_cliente()


class MeuDateInput(forms.DateInput):
    input_type = 'date'


class CadastraParametro(forms.ModelForm):
    class Meta:
        model = Parametros
        fields = ['Chave', 'Valor']
        widgets = {'Chave': forms.Select(choices=parametros_chave, attrs={'class': 'form-control'}),
                   'Valor': forms.TextInput(attrs={'class': 'form-control'})}


class CadastraFeriado(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraFeriado, self).__init__(*args, **kwargs)
        self.fields['Chave'].initial = 'FERIADO'

    class Meta:
        model = Parametros
        fields = ['Chave', 'Valor']
        widgets = {'Chave': forms.HiddenInput(),
                   'Valor': MeuDateInput(format='%Y-%m-%d', attrs={'class': 'form-control'})}


class CadastraParametroTabelaPadrao(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraParametroTabelaPadrao, self).__init__(*args, **kwargs)
        self.fields['Chave'].initial = 'TABELA PADRAO'

    class Meta:
        model = Parametros
        fields = ['idParametro', 'Chave', 'Valor']
        widgets = {'Chave': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'True'}),
                   'Valor': forms.Select(choices=fantasia, attrs={'class': 'form-control'})}


class FormFileUpload(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['DescricaoUpload', 'uploadFile']
        widgets = {'DescricaoUpload': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'True'}),
                   'uploadFile': forms.FileInput(),
                   }
