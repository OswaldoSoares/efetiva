from django import forms
from .models import Minuta, MinutaColaboradores, MinutaItens, MinutaNotas
from veiculos.models import Veiculo
from pessoas.models import Pessoal
from django.db.models import Value
from django.db.models.functions import Concat
from django.core.exceptions import ValidationError
from datetime import timedelta
import datetime


class MeuDateInput(forms.DateInput):
    input_type = 'date'


class MeuTimeInput(forms.TimeInput):
    input_type = 'time'


class CadastraMinuta(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraMinuta, self).__init__(*args, **kwargs)
        self.fields['DataMinuta'].initial = datetime.date.today()
        self.fields['HoraInicial'].initial = '06:00'
        # Personaliza opcão o do SELECT
        self.fields['idCliente'].empty_label = 'Selecione um item da lista'
        self.fields['idCategoriaVeiculo'].empty_label = 'Selecione um item da lista'

    class Meta:
        model = Minuta
        fields = ('Minuta', 'idCliente', 'DataMinuta', 'HoraInicial', 'idCategoriaVeiculo', 'Coleta', 'Entrega',
                  'Obs', 'StatusMinuta')
        labels = {'idCliente': 'CLIENTE', 'DataMinuta': 'DATA DA MINUTA', 'HoraInicial': 'HORA INICIAL',
                  'idCategoriaVeiculo': 'VEÍCULO SOLICITADO', 'Coleta': 'COLETA', 'Entrega': 'ENTREGA',
                  'Obs': 'OBSERVAÇÕES'}
        widgets = {'Minuta': forms.HiddenInput(), 'idCliente': forms.Select(attrs={'class': 'formfields'}),
                   'DataMinuta': MeuDateInput(format='%Y-%m-%d', attrs={'class': 'formfields', 'value': '01/09/2020'}),
                   'HoraInicial': MeuTimeInput(attrs={'class': 'formfields'}),  'idCategoriaVeiculo': forms.Select(
                attrs={'class': 'formfields'}), 'Coleta': forms.Textarea(attrs={'class': 'formfieldstexto'}),
                   'Entrega': forms.Textarea(attrs={'class': 'formfieldstexto'}), 'Obs': forms.Textarea(attrs={
                'class': 'formfieldstexto'}), 'StatusMinuta': forms.HiddenInput()}


class CadastraMinutaMotorista(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraMinutaMotorista, self).__init__(*args, **kwargs)
        self.fields['idPessoal'].queryset = Pessoal.objects.exclude(Categoria='AJUDANTE')
        # Personaliza opcão o do SELECT
        self.fields['idPessoal'].empty_label = 'Selecione um item da lista'

    class Meta:
        model = MinutaColaboradores
        fields = ('idPessoal', 'idMinuta', 'Cargo')
        labels = {'idPessoal': 'MOTORISTA'}
        widgets = {'idPessoal': forms.Select(attrs={'class': 'formfields'}), 'idMinuta': forms.HiddenInput(),
                   'Cargo': forms.HiddenInput()}


class CadastraMinutaAjudante(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraMinutaAjudante, self).__init__(*args, **kwargs)
        self.fields['idPessoal'].queryset = Pessoal.objects.all()
        # Personaliza opcão o do SELECT
        self.fields['idPessoal'].empty_label = 'Selecione um item da lista'

    class Meta:
        model = MinutaColaboradores
        fields = ('idPessoal', 'idMinuta', 'Cargo' )
        labels = {'idPessoal': 'AJUDANTE'}
        widgets = {'idPessoal': forms.Select(attrs={'class': 'formfields'}), 'idMinuta': forms.HiddenInput(),
                   'Cargo': forms.HiddenInput()}


class CadastraMinutaVeiculo(forms.Form):
    # Cria um queryset do Model Veiculo e adiciona um field "Virtual" concatenado (Veiculo)
    qs = Veiculo.objects.annotate(
        Veiculo=Concat('Marca', Value(' - '), 'Modelo', Value(' - '), 'Placa')).filter(Motorista=0)
    choice = [('0', 'Selecione um item da lista...')] + [(x.idVeiculo, x.Veiculo) for x in qs]

    idMinuta = forms.IntegerField(widget=forms.HiddenInput())
    Propriedade = forms.CharField(label='PROPRIEDADE', widget=forms.Select(choices=(
                ('0', 'Selecione um item da lista...'), ('1', 'VEÍCULO PRÓPRIO'), ('2', 'VEÍCULOS TRANSPORTADORA'),
                ('3', 'VEÍCULOS CADASTRADOS')), attrs={'class': 'formfields', 'data-url':
        '/minutas/filtraminutaveiculo'}))
    Veiculo = forms.CharField(required=True, label='VEÍCULO', widget=forms.Select(choices=(choice), attrs={
                'class': 'formfields'}))


class CadastraMinutaHoraFinal(forms.ModelForm):
    class Meta:
        model = Minuta
        fields = {'idMinuta', 'HoraFinal'}
        widgets = {'HoraFinal': MeuTimeInput(attrs={'class': 'formfieldshort'})}


class CadastraMinutaHoraCobra(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraMinutaHoraCobra, self).__init__(*args, **kwargs)
        self.fields['Tempo'].initial = timedelta()

    class Meta:
        model = MinutaItens
        fields = {'idMinuta', 'Descricao', 'TipoItens', 'Tempo'}
        widgets = {'Descricao': forms.HiddenInput(), 'Valor': forms.HiddenInput(), 'idMinuta': forms.HiddenInput(),
                   'TipoItens': forms.HiddenInput(), 'Tempo': MeuTimeInput()}


class CadastraMinutaHoraExcede(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraMinutaHoraExcede, self).__init__(*args, **kwargs)
        self.fields['Tempo'].initial = timedelta()
        self.fields['Porcento'].initial = 100

    class Meta:
        model = MinutaItens
        fields = {'idMinuta', 'Descricao', 'TipoItens', 'RecebePaga', 'Tempo', 'Porcento'}
        widgets = {'idMinuta': forms.HiddenInput(), 'Descricao': forms.HiddenInput(),
                   'TipoItens': forms.HiddenInput(), 'RecebePaga': forms.HiddenInput(), 'Tempo': MeuTimeInput(),
                   'Porcento': forms.NumberInput(attrs={'class': 'formfield porcentagem', 'step': '1.00'}),
                   'Valor': forms.HiddenInput()}

    field_order = ['Tempo', 'Porcento']


class CadastraMinutaKMInicial(forms.ModelForm):
    class Meta:
        model = Minuta
        fields = {'KMInicial'}
        widgets = {'KMInicial': forms.NumberInput(attrs={'class': 'formfieldshort'})}


class CadastraMinutaKMFinal(forms.ModelForm):
    def clean(self):
        cleaned_data = super(CadastraMinutaKMFinal, self).clean()
        if cleaned_data.get('KMFinal') <= cleaned_data.get('KMInicial'):
            raise ValidationError("A KM final não pode ser igual ou menor que a KM inicial")

    class Meta:
        model = Minuta
        fields = ('KMInicial', 'KMFinal',)
        widgets = {'KMInicial': forms.HiddenInput(attrs={'class': 'formfieldshort'}),
                   'KMFinal': forms.NumberInput(attrs={'class': 'formfieldshort'})}


class CadastraMinutaItens(forms.ModelForm):
    class Meta:
        model = MinutaItens
        fields = {'idMinuta', 'Descricao', 'TipoItens', 'Valor', 'Quantidade', 'Porcento', 'Tempo',}
        widgets = {'Descricao': forms.TextInput(attrs={'class': 'formfields'})}


class CadastraMinutaDespesa(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraMinutaDespesa, self).__init__(*args, **kwargs)
        self.fields['Tempo'].initial = timedelta()

    class Meta:
        model = MinutaItens
        fields = {'idMinuta', 'Descricao', 'Valor', 'TipoItens', 'Tempo', 'RecebePaga',}
        widgets = {'Descricao': forms.Select(attrs={'class': 'formfieldsshort'}),
                   'Valor': forms.NumberInput(attrs={'class': 'formfieldsshort'}),
                   'idMinuta': forms.HiddenInput(), 'TipoItens': forms.HiddenInput(), 'Tempo': forms.HiddenInput(),
                   'RecebePaga': forms.HiddenInput(),}


class CadastraMinutaParametroDespesa(forms.Form):
    Despesa = forms.CharField( label='DESPESA', widget=forms.TextInput(attrs={'class': 'formfields'}))
    idMinuta = forms.IntegerField(widget=forms.HiddenInput())


class CadastraMinutaNota(forms.ModelForm):
    def __init__(self, idminuta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = MinutaNotas.objects.filter(idMinuta=idminuta)
        self.fields['NotaGuia'] = forms.ChoiceField(choices=[('0', '  ')] + [(x.Nota, x.Nota) for x in qs])
        self.fields['NotaGuia'].widget.attrs = {'class': 'formfields'}
        self.fields['NotaGuia'].label = 'NOTA GUIA'

    class Meta:
        model = MinutaNotas
        fields = {'idMinutaNotas', 'Nota', 'ValorNota', 'Peso', 'Volume', 'Nome', 'Estado', 'Cidade', 'NotaGuia',
                  'idMinuta'}
        labels = {'Nota': 'NOTA', 'Valor': 'VALOR', 'Peso': 'PESO', 'Volume': 'VOLUME', 'Nome': 'RAZÃO SOCIAL',
                  'Estado': 'ESTADO', 'Cidade': 'CIDADE'}
        widgets = {'Nota': forms.TextInput(attrs={'class': 'formfields'}),
                   'ValorNota': forms.NumberInput(attrs={'class': 'formfields'}),
                   'Peso': forms.NumberInput(attrs={'class': 'formfields'}),
                   'Volume': forms.NumberInput(attrs={'class': 'formfields'}),
                   'Nome': forms.TextInput(attrs={'class': 'formfields'}),
                   'Estado': forms.TextInput(attrs={'class': 'formfields'}),
                   'Cidade': forms.TextInput(attrs={'class': 'formfields'}),
                   'idMinuta': forms.HiddenInput()}
    field_order = ['Nota', 'ValorNota', 'Peso', 'Volume', 'NotaGuia', 'Nome', 'Estado', 'Cidade']


class CadastraMinutaFatura(forms.ModelForm):
    class Meta:
        model = Minuta
        fields = {'idMinuta', 'Valor', 'Comentarios', 'idFatura'}


class CadastraComentarioMinuta(forms.ModelForm):
    class Meta:
        model = Minuta
        fields = {'Comentarios'}
        widgets = {'Comentarios': forms.Textarea(attrs={'rows': 5, 'class': 'comentarios'})}
