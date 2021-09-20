import datetime

from django import forms
from .models import Pessoal, DocPessoal, FonePessoal, ContaPessoal, Salario, Vales, ContraCheque, ContraChequeItens


CATEGORIAS = [('', ''), ('AGREGADO', 'AGREGADO'), ('AJUDANTE', 'AJUDANTE'), ('FUNCIONÁRIO', 'FUNCIONÁRIO'),
              ('MOTORISTA', 'MOTORISTA'), ('PROPRIETÁRIO', 'PROPRIETÁRIO')]

TIPOPGTO = [('', ''), ('MENSALISTA', 'MENSALISTA'), ('SAIDA', 'SAIDA'), ('MINUTA', 'MINUTA')]

TIPODOC = [('', ''), ('RG', 'RG'), ('CPF', 'CPF',), ('HABILITAÇÃO', 'HABILITAÇÃO'), ('RESERVISTA', 'RESERVISTA'),
           ('PASSAPORTE', 'PASSAPORTE'), ('PIS/PASEP', 'PISPASEP')]

TIPOFONE = [('', ''), ('WHATSAPP', 'WHATSAPP'), ('VIVO', 'VIVO'), ('TIM', 'TIM'), ('OI', 'OI'), ('NEXTEL', 'NEXTEL'),
            ('CLARO', 'CLARO'), ('FIXO', 'FIXO'), ('RECADO', 'RECADO')]

TIPOCONTA = [('', ''), ('CORRENTE', 'CORRENTE'), ('POUPANÇA', 'POUPANÇA')]

MESREFERENCIA = [('1', 'JANEIRO'), ('2', 'FEVEREIRO'), ('3', 'MARÇO'), ('4', 'ABRIL'), ('5', 'MAIO'), ('6', 'JUNHO'),
                 ('7', 'JULHO'), ('8', 'AGOSTO'), ('9', 'SETEMBRO'), ('10', 'OUTUBRO'), ('11', 'NOVEMBRO'),
                 ('12', 'DEZEMBRO')]

hoje = datetime.date.today()
ANOREFERENCIA = [(hoje.year-1, hoje.year-1), (hoje.year, hoje.year), (hoje.year+1, hoje.year+1)]


class MeuDateInput(forms.DateInput):
    input_type = 'date'


class CadastraPessoal(forms.ModelForm):
    class Meta:
        model = Pessoal
        fields = ('Nome', 'Endereco', 'Bairro', 'CEP', 'Cidade', 'Estado', 'DataNascimento', 'Mae', 'Pai',
                  'DataAdmissao', 'Categoria', 'TipoPgto', 'Foto')
        labels = {'Nome': 'NOME', 'Endereco': 'ENDEREÇO', 'Bairro': 'BAIRRO', 'CEP': 'CEP', 'Cidade': 'CIDADE',
                  'Estado': 'ESTADO', 'DataNascimento': 'DATA DE NASCIMENTO', 'Mae': 'NOME DA MÃE',
                  'Pai': 'NOME DO PAI', 'DataAdmissao': 'DATA DE ADMISSÃO', 'Categoria': 'CATEGORIA',
                  'TipoPgto': 'TIPO DE PAGAMENTO', 'Foto': 'FOTO DO COLABORADOR'}
        widgets = {'Nome': forms.TextInput(attrs={'class': 'form-control'}),
                   'Endereco': forms.TextInput(attrs={'class': 'form-control'}),
                   'Bairro': forms.TextInput(attrs={'class': 'form-control'}),
                   'CEP': forms.TextInput(attrs={'class': 'form-control'}),
                   'Cidade': forms.TextInput(attrs={'class': 'form-control'}),
                   'Estado': forms.TextInput(attrs={'class': 'form-control'}),
                   'DataNascimento': MeuDateInput(format='%Y-%m-%d',
                                                  attrs={'class': 'form-control', 'max': '2020/01/29'}),
                   'Mae': forms.TextInput(attrs={'class': 'form-control'}),
                   'Pai': forms.TextInput(attrs={'class': 'form-control'}),
                   'DataAdmissao': MeuDateInput(format='%Y-%m-%d',
                                                attrs={'class': 'form-control', 'max': '2020/01/29'}),
                   'Categoria': forms.Select(attrs={'class': 'form-control'}, choices=CATEGORIAS),
                   'TipoPgto': forms.Select(attrs={'class': 'form-control'}, choices=TIPOPGTO)}


class CadastraDocPessoal(forms.ModelForm):
    class Meta:
        model = DocPessoal
        fields = ('TipoDocumento', 'Documento', 'Data', 'idPessoal')
        labels = {'TipoDocumento': 'TIPO DE DOCUMENTO', 'Documento': 'DOCUMENTO', 'Data': 'DATA EMISSÃO OU VENCIMENTO'}
        widgets = {'TipoDocumento': forms.Select(attrs={'class': 'formfields'}, choices=TIPODOC),
                   'Documento': forms.TextInput(attrs={'class': 'formfields'}),
                   'Data': MeuDateInput(format='%Y-%m-%d', attrs={'class': 'formfields'}),
                   'idPessoal': forms.HiddenInput()}


class CadastraFonePessoal(forms.ModelForm):
    class Meta:
        model = FonePessoal
        fields = ('TipoFone', 'Fone', 'Contato', 'idPessoal')
        labels = {'TipoFone': 'OPERADORA', 'Fone': 'TELEFONE', 'Contato': 'CONTATO'}
        widgets = {'TipoFone': forms.Select(attrs={'class': 'formfields'}, choices=TIPOFONE),
                   'Fone': forms.TextInput(attrs={'class': 'formfields'}),
                   'Contato': forms.TextInput(attrs={'class': 'formfields'}), 'idPessoal': forms.HiddenInput()}


class CadastraContaPessoal(forms.ModelForm):
    class Meta:
        model = ContaPessoal
        fields = ('Banco', 'Agencia', 'Conta', 'TipoConta', 'Titular', 'Documento', 'PIX', 'idPessoal')
        labels = {'Banco': 'BANCO', 'Agencia': 'AGÊNCIA', 'Conta': 'CONTA', 'TipoConta': 'TIPO DA CONTA',
                  'PIX': 'CHAVE PIX', 'Titular': 'TITULAR DA CONTA', 'Documento': 'CPF DO TITULAR'}
        widgets = {'Banco': forms.TextInput(attrs={'class': 'formfields'}),
                   'Agencia': forms.TextInput(attrs={'class': 'formfields'}),
                   'Conta': forms.TextInput(attrs={'class': 'formfields'}),
                   'TipoConta': forms.Select(attrs={'class': 'formfields'}, choices=TIPOCONTA),
                   'PIX': forms.TextInput(attrs={'class': 'formfields'}),
                   'Titular': forms.TextInput(attrs={'class': 'formfields'}),
                   'Documento': forms.TextInput(attrs={'class': 'formfields'}), 'idPessoal': forms.HiddenInput()}


class CadastraSalario(forms.ModelForm):
    class Meta:
        model = Salario
        fields = ('idPessoal', 'Salario', 'HorasMensais', 'ValeTransporte')
        labels = {'Salario': 'formfields', 'HorasMensais': 'HORAS MENSAIS', 'ValeTransporte': 'VALE TRANSPORTE'}
        widgets = {'Salario': forms.NumberInput(attrs={'class': 'form-control'}), 'idPessoal': forms.HiddenInput(),
                   'HorasMensais': forms.NumberInput(attrs={'class': 'form-control'}),
                   'ValeTransporte': forms.NumberInput(attrs={'class': 'form-control'})}


class CadastraVale(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraVale, self).__init__(*args, **kwargs)
        self.fields['Data'].initial = datetime.date.today()

    class Meta:
        model = Vales
        fields = ('idPessoal', 'Data', 'Descricao', 'Valor')
        labels = {'Data': 'DATA', 'Descricao': 'DESCRIÇÃo', 'Valor': 'VALOR', 'idPessoal': 'COLABORADOR'}
        widgets = {'Data': MeuDateInput(format='%Y-%m-%d', attrs={'class': 'form-control'}),
                   'Descricao': forms.TextInput(attrs={'class': 'form-control'}),
                   'Valor': forms.NumberInput(attrs={'class': 'form-control'}),
                   'idPessoal': forms.Select(attrs={'class': 'form-control'})}


class CadastraContraCheque(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CadastraContraCheque, self).__init__(*args, **kwargs)
        self.fields['MesReferencia'].initial = hoje.month
        self.fields['AnoReferencia'].initial = hoje.year

    class Meta:
        model = ContraCheque
        fields = ('MesReferencia', 'AnoReferencia', 'Valor', 'idPessoal')
        labels = {'MesReferencia': 'MÊS REFERÊNCIA', 'AnoReferencia': 'ANO REFERÊNCIA'}
        widgets = {'MesReferencia': forms.Select(attrs={'class': 'form-control'}, choices=MESREFERENCIA),
                   'AnoReferencia': forms.Select(attrs={'class': 'form-control'}, choices=ANOREFERENCIA)}


class CadastraContraChequeItens(forms.ModelForm):
    class Meta:
        model = ContraChequeItens
        fields = ('Descricao', 'Valor', 'Registro', 'idContraCheque')
        lables = {'Descricao': 'DESCRIÇÃO', 'Valor': 'VALOR'}
        widgets = {'Descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DESCRIÇÃO'}),
                   'Valor': forms.NumberInput(attrs={'class': 'form-control'}),
                   'Registro': forms.Select(attrs={'class': 'form-control'}, choices=[('C', 'CRÉDITO'),
                                                                                      ('D', 'DÉBITO')])}


class CadastraDemissao(forms.ModelForm):
    class Meta:
        model = Pessoal
        fields = ('DataDemissao',)
        widgets = {'DataDemissao': MeuDateInput(format='%Y-%m-%d', attrs={'class': 'form-control'})}
