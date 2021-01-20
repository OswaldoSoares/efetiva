from django import forms
from .models import Cliente, FoneContatoCliente, EMailContatoCliente, Cobranca, Tabela, TabelaVeiculo, \
    TabelaCapacidade, TabelaPerimetro, FormaPagamento

TIPOFONE = [
    ('WHATSAPP', 'WHATSAPP'),
    ('VIVO', 'VIVO'),
    ('TIM', 'TIM'),
    ('OI', 'OI'),
    ('NEXTEL', 'NEXTEL'),
    ('CLARO', 'CLARO'),
    ('FIXO', 'FIXO'),
    ('RECADO', 'RECADO'),
]


class MeuTimeInput(forms.TimeInput):
    input_type = 'time'


class CadastraCliente(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('Fantasia',
                  'Nome',
                  'Endereco',
                  'Bairro',
                  'CEP',
                  'Cidade',
                  'Estado',
                  'CNPJ',
                  'IE',
                  'Site',
                  'idCliente',
                  )
        labels = {
            'Fantasia': 'NOME FANTASIA',
            'Nome': 'RAZÃO SOCIAL',
            'Endereco': 'ENDEREÇO',
            'Bairro': 'BAIRRO',
            'CEP': 'CEP',
            'Cidade': 'CIDADE',
            'Estado': 'ESTADO',
            'CNPJ': 'CNPJ',
            'IE': 'INSCRIÇÃO ESTADUAL',
            'Site': 'SITE',
        }
        widgets = {
            'Fantasia': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'FANTASIA',
                }
            ),
            'Nome': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'NOME',
                }
            ),
            'Endereco': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'ENDEREÇO',
                }
            ),
            'Bairro': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'BAIRRO',
                }
            ),
            'CEP': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CEP',
                }
            ),
            'Cidade': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CIDADE',
                }
            ),
            'Estado': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'ESTADO',
                }
            ),
            'CNPJ': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CNPJ',
                }
            ),
            'IE': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'IE',
                }
            ),
            'Site': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'SITE'
                }
            ),
        }


class CadastraFoneContatoCliente(forms.ModelForm):
    class Meta:
        model = FoneContatoCliente
        fields = ('Contato',
                  'TipoFone',
                  'Fone',
                  'idCliente'
                  )
        labels = {
            'Contato': 'CONTATO',
            'TipoFone': 'OPERADORA',
            'Fone': 'TELEFONE',
        }
        widgets = {
            'Contato': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CONTATO',
                }
            ),
            'TipoFone': forms.Select(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'OPERADORA',
                },
                choices=TIPOFONE
            ),
            'Fone': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'TELEFONE',
                }
            ),
            'idCliente': forms.HiddenInput(
            )
        }


class CadastraEMailContatoCliente(forms.ModelForm):
    class Meta:
        model = EMailContatoCliente
        fields = ('Contato', 'EMail', 'RecebeFatura', 'idCliente')
        labels = {'Contato': 'CONTATO', 'EMail': 'E-MAIL', 'RcebeFatura': 'RECEBE FATURA'}
        widgets = {'Contato': forms.TextInput(attrs={'class': 'formfields'}),
                   'EMail': forms.EmailInput(attrs={'class': 'formfields'}),
                   'RecebeFatura': forms.CheckboxInput(), 'idCliente': forms.HiddenInput()}


class CadastraCobranca(forms.ModelForm):
    class Meta:
        model = Cobranca
        fields = ('Nome',
                  'Endereco',
                  'Bairro',
                  'CEP',
                  'Cidade',
                  'Estado',
                  'CNPJ',
                  'IE',
                  'idCliente')
        labels = {
            'Nome': 'RAZÃO SOCIAL',
            'Endereco': 'ENDEREÇO',
            'Bairro': 'BAIRRO',
            'CEP': 'CEP',
            'Cidade': 'CIDADE',
            'Estado': 'ESTADO',
            'CNPJ': 'CNPJ',
            'IE': 'INSCRIÇÃO ESTADUAL',
        }
        widgets = {
            'Nome': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'NOME',
                }
            ),
            'Endereco': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'ENDEREÇO',
                }
            ),
            'Bairro': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'BAIRRO',
                }
            ),
            'CEP': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CEP',
                }
            ),
            'Cidade': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CIDADE',
                }
            ),
            'Estado': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'ESTADO',
                }
            ),
            'CNPJ': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CNPJ',
                }
            ),
            'IE': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'IE',
                }
            ),
            'idCliente': forms.HiddenInput(
            )
        }


class CadastraTabela(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraTabela, self).__init__(*args, **kwargs)
        # Personaliza opcão o do SELECT
        self.fields['idFormaPagamento'].empty_label = 'Selecione um item da lista'

    class Meta:
        model = Tabela
        fields = ('Comissao',
                  'TaxaExpedicao',
                  'AjudanteCobra',
                  'AjudantePaga',
                  'EntregaCobra',
                  'EntregaKGCobra',
                  'EntregaVolumeCobra',
                  'EntregaPaga',
                  'EntregaKGPaga',
                  'EntregaVolumePaga',
                  'idFormaPagamento',
                  'idCliente'
                  )
        labels = {
            'Comissao': 'PORCENTAGEM DA COMISSÃO',
            'TaxaExpedicao': 'TAXA EXPEDIÇÃO',
            'AjudanteCobra': 'VALOR AJUDANTE À RECEBER',
            'AjudantePaga': 'VALOR AJUDANTE À PAGAR',
            'EntregaCobra': 'VALOR ENTREGA À RECEBER',
            'EntregaKGCobra': 'VALOR ENTREGA KG À RECEBER',
            'EntregaVolumeCobra': 'VALOR ENTREGA VOLUME À RECEBER',
            'EntregaPaga': 'VALOR ENTREGA À PAGAR',
            'EntregaKGPaga': 'VALOR ENTREGA KG À PAGAR',
            'EntregaVolumePaga': 'VALOR ENTREGA VOLUME À PAGAR',
            'idFormaPagamento': 'FORMA DE PAGAMENTO',
        }
        widgets = {
            'Comissao': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'COMISSÃO',
                }
            ),
            'TaxaExpedicao': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'TAXA DE EXPEDIÇÃO'
                }
            ),
            'AjudanteCobra': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR AJUDANTE À RECEBER'
                }
            ),
            'AjudantePaga': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR AJUDANTE À PAGAR'
                }
            ),
            'EntregaCobra': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR ENTREGA À RECEBER'
                }
            ),
            'EntregaKGCobra': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR ENTREGA À RECEBER'
                }
            ),
            'EntregaVolumeCobra': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR ENTREGA À RECEBER'
                }
            ),
            'EntregaPaga': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR ENTREGA À RECEBER'
                }
            ),
            'EntregaKGPaga': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR ENTREGA À RECEBER'
                }
            ),
            'EntregaVolumePaga': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'VALOR ENTREGA À RECEBER'
                }
            ),
            'idFormaPagamento': forms.Select(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'FORMA DE PAGAMENTO',
                }
            ),
            'idCliente': forms.HiddenInput(
            )
        }


class CadastraTabelaVeiculo(forms.ModelForm):
    class Meta:
        fields = ('PorcentagemCobra', 'PorcentagemPaga', 'HoraCobra', 'HoraPaga', 'HoraMinimo', 'KMCobra', 'KMPaga',
                  'KMMinimo', 'EntregaCobra', 'EntregaPaga', 'EntregaMinimo', 'EntregaKGCobra', 'EntregaKGPaga',
                  'EntregaVolumeCobra', 'EntregaVolumePaga', 'SaidaCobra', 'SaidaPaga' , 'idCliente',
                  'idCategoriaVeiculo')
        model = TabelaVeiculo
        labels = {
            'PorcentagemCobra': 'PORCENTAGEM DAS NOTAS À RECEBER',
            'PorcentagemPaga': 'PORCENTAGEM DAS NOTAS À PAGAR',
            'HoraCobra': 'VALOR DA HORA À RECEBER',
            'HoraPaga': 'VALOR DA HORA À PAGAR',
            'HoraMinimo': 'MÍNIMO DE HORAS',
            'KMCobra': 'VALOR DO KILOMETRO À RECEBER',
            'KMPaga': 'VALOR DO KILOMETRO À PAGAR',
            'KMMinimo': 'MÍNIMO DE KILOMETROS',
            'EntregaCobra': 'VALOR DA ENTREGA À RECEBER',
            'EntregaPaga': 'VALOR DA ENTREGA À PAGAR',
            'EntregaMinimo': 'MÍNIMO DE ENTREGAS',
            'EntregaKGCobra': 'VALOR KG À RECEBER',
            'EntregaKGPaga': 'VALOR KG À PAGAR',
            'EntregaVolumeCobra': 'VALOR VOLUME À RECEBER',
            'EntregaVolumePaga': 'VALOR VOLUME À PAGAR',
            'SaidaCobra': 'VALOR DA SAÍDA À RECEBER',
            'SaidaPaga': 'VALOR DA SAÍDA À PAGAR'
        }
        widgets = {
            'PorcentagemCobra': forms.NumberInput(attrs={'class': 'formfields', 'step': '1'}),
            'PorcentagemPaga': forms.NumberInput(attrs={'class': 'formfields'}),
            'HoraCobra': forms.NumberInput(attrs={'class': 'formfields'}),
            'HoraPaga': forms.NumberInput(attrs={'class': 'formfields'}),
            'HoraMinimo': MeuTimeInput(attrs={'class': 'formfields'}),
            'KMCobra': forms.NumberInput(attrs={'class': 'formfields'}),
            'KMPaga': forms.NumberInput(attrs={'class': 'formfields'}),
            'KMMinimo': forms.NumberInput(attrs={'class': 'formfields'}),
            'EntregaCobra': forms.NumberInput(attrs={'class': 'formfields'}),
            'EntregaPaga': forms.NumberInput(attrs={'class': 'formfields'}),
            'EntregaMinimo': forms.NumberInput(attrs={'class': 'formfields'}),
            'EntregaKGCobra': forms.NumberInput(attrs={'class': 'formfields'}),
            'EntregaKGPaga': forms.NumberInput(attrs={'class': 'formfields'}),
            'EntregaVolumeCobra': forms.NumberInput(attrs={'class': 'formfields'}),
            'EntregaVolumePaga': forms.NumberInput(attrs={'class': 'formfields'}),
            'SaidaCobra': forms.NumberInput(attrs={'class': 'formfields'}),
            'SaidaPaga': forms.NumberInput(attrs={'class': 'formfields'}),
            'idCliente': forms.HiddenInput(attrs={}),
            'idCategoriaVeiculo': forms.HiddenInput(attrs={}),
        }


class CadastraTabelaCapacidade(forms.ModelForm):
    class Meta:
        model = TabelaCapacidade
        fields = ('CapacidadeInicial', 'CapacidadeFinal', 'CapacidadeCobra', 'CapacidadePaga', 'idCliente'
                  )
        labels = {
            'CapacidadeInicial': 'CAPACIDADE (KGs) INICIAL',
            'CapacidadeFinal': 'CAPACIDADE (KGs) FINAL',
            'CapacidadeCobra': 'CAPACIDADE COBRA',
            'CapacidadePaga': 'CAPACIDADE PAGA',
        }
        widgets = {
            'CapacidadeInicial': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CAPACIDADE (KGs) INICIAL:',
                    'readonly': True,
                }
            ),
            'CapacidadeFinal': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CAPACIDADE (KGs) FINAL:',
                }
            ),
            'CapacidadeCobra': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CAPACIDADE COBRA:',
                }
            ),
            'CapacidadePaga': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'CAPACIDADE PAGA:',
                }
            ),
            'idCliente': forms.HiddenInput(
            )
        }


class CadastraTabelaPerimetro(forms.ModelForm):
    class Meta:
        model = TabelaPerimetro
        fields = ('PerimetroInicial',
                  'PerimetroFinal',
                  'PerimetroCobra',
                  'PerimetroPaga',
                  'idCliente'
                  )
        labels = {
            'PerimetroInicial': 'PERIMETRO (KMs) INICIAL',
            'PerimetroFinal': 'PERIMETRO (KMs) FINAL',
            'PerimetroCobra': 'PERIMETRO COBRA',
            'PerimetroPaga': 'PERIMETRO PAGA',
        }
        widgets = {
            'PerimetroInicial': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'PERIMETRO (KMs) INICIAL:',
                    'readonly': True,
                }
            ),
            'PerimetroFinal': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'PERIMETRO (KMs) FINAL:',
                }
            ),
            'PerimetroCobra': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'PERIMETRO COBRA:',
                }
            ),
            'PerimetroPaga': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'PERIMETRO PAGA:',
                }
            ),
            'idCliente': forms.HiddenInput(
            )
        }


class CadastraFormaPgto(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = {
            'Forma',
            'Dias'
        }
        labels = {
            'Forma': 'FORMA',
            'Dias': 'DIAS'
        }
        widgets = {
            'Forma': forms.TextInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'PERÍODO PARA FATURAR ',
                }
            ),
            'Dias': forms.NumberInput(
                attrs={
                    'class': 'formfields',
                    # 'placeholder': 'DIAS PARA PAGAR'
                }
            )
        }