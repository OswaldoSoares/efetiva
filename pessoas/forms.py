from django import forms
from .models import Pessoal, DocPessoal, FonePessoal, ContaPessoal


CATEGORIAS = [
    ('', ''),
    ('AGREGADO', 'AGREGADO'),
    ('AJUDANTE', 'AJUDANTE'),
    ('FUNCIONÁRIO', 'FUNCIONÁRIO'),
    ('MOTORISTA', 'MOTORISTA'),
    ('PROPRIETÁRIO', 'PROPRIETÁRIO'),
]

TIPOPGTO = [
    ('', ''),
    ('MENSAL - BANCO DE HORAS', 'MENSAL - BANCO DE HORAS'),
    ('SAIDA', 'SAIDA'),
    ('MINUTA', 'MINUTA'),
]

TIPODOC = [
    ('', ''),
    ('RG', 'RG'),
    ('CPF', 'CPF',),
    ('HABILITAÇÃO', 'HABILITAÇÃO'),
    ('RESERVISTA', 'RESERVISTA'),
    ('PASSAPORTE', 'PASSAPORTE'),
    ('PIS/PASEP', 'PISPASEP'),
]

TIPOFONE = [
    ('', ''),
    ('WHATSAPP', 'WHATSAPP'),
    ('VIVO', 'VIVO'),
    ('TIM', 'TIM'),
    ('OI', 'OI'),
    ('NEXTEL', 'NEXTEL'),
    ('CLARO', 'CLARO'),
    ('FIXO', 'FIXO'),
    ('RECADO', 'RECADO'),
]

TIPOCONTA = [
    ('', ''),
    ('CORRENTE', 'CORRENTE'),
    ('POUPANÇA', 'POUPANÇA'),
]


class MeuDateInput(forms.DateInput):
    input_type = 'date'


class CadastraPessoal(forms.ModelForm):
    class Meta:
        model = Pessoal
        fields = ('Nome',
                  'Endereco',
                  'Bairro',
                  'CEP',
                  'Cidade',
                  'Estado',
                  'DataNascimento',
                  'Mae',
                  'Pai',
                  'Categoria',
                  'TipoPgto',
                  'Foto'
                  )
        labels = {
            'Nome': 'NOME',
            'Endereco': 'ENDEREÇO',
            'Bairro': 'BAIRRO',
            'CEP': 'CEP',
            'Cidade': 'CIDADE',
            'Estado': 'ESTADO',
            'DataNascimento': 'DATA DE NASCIMENTO',
            'Mae': 'NOME DA MÃE',
            'Pai': 'NOME DO PAI',
            'Categoria': 'CATEGORIA',
            'TipoPgto': 'TIPO DE PAGAMENTO',
            'Foto': 'FOTO DO COLABORADOR',
        }
        widgets = {
            'Nome': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'Endereco': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'Bairro': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'CEP': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'Cidade': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'Estado': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'DataNascimento': MeuDateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class': 'formfields',
                    'max': '2020/01/29',
                },
            ),
            'Mae': forms.TextInput(
                attrs={
                    'class': 'formfields',
                },
            ),
            'Pai': forms.TextInput(
                attrs={
                    'class': 'formfields',
                },
            ),
            'Categoria': forms.Select(
                attrs={
                    'class': 'formfields',
                },
                choices=CATEGORIAS
            ),
            'TipoPgto': forms.Select(
                attrs={
                    'class': 'formfields',
                },
                choices=TIPOPGTO
            ),

        }


class CadastraDocPessoal(forms.ModelForm):
    class Meta:
        model = DocPessoal
        fields = ('TipoDocumento',
                  'Documento',
                  'Data',
                  'idPessoal'
                  )
        labels = {
            'TipoDocumento': 'TIPO DE DOCUMENTO',
            'Documento': 'DOCUMENTO',
            'Data': 'DATA EMISSÃO OU VENCIMENTO',
        }
        widgets = {
            'TipoDocumento': forms.Select(
                attrs={
                    'class': 'formfields',
                },
                choices=TIPODOC
            ),
            'Documento': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'Data': MeuDateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class': 'formfields',
                }
            ),
            'idPessoal': forms.HiddenInput(
            )
        }


class CadastraFonePessoal(forms.ModelForm):
    class Meta:
        model = FonePessoal
        fields = ('TipoFone',
                  'Fone',
                  'Contato',
                  'idPessoal'
                  )
        labels = {
            'TipoFone': 'OPERADORA',
            'Fone': 'TELEFONE',
            'Contato': 'CONTATO'
        }
        widgets = {
            'TipoFone': forms.Select(
                attrs={
                    'class': 'formfields',
                },
                choices=TIPOFONE
            ),
            'Fone': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'Contato': forms.TextInput(
                attrs={
                    'class': 'formfields',
                }
            ),
            'idPessoal': forms.HiddenInput(
            )
        }


class CadastraContaPessoal(forms.ModelForm):
    class Meta:
        model = ContaPessoal
        fields = ('Banco', 'Agencia', 'Conta', 'TipoConta', 'Titular', 'Documento', 'PIX', 'idPessoal')
        labels = {
            'Banco': 'BANCO',
            'Agencia': 'AGÊNCIA',
            'Conta': 'CONTA',
            'TipoConta': 'TIPO DA CONTA',
            'PIX': 'CHAVE PIX',
            'Titular': 'TITULAR DA CONTA',
            'Documento': 'CPF DO TITULAR',
        }
        widgets = {
            'Banco': forms.TextInput(attrs={'class': 'formfields'}),
            'Agencia':forms.TextInput(attrs={'class': 'formfields'}),
            'Conta': forms.TextInput(attrs={'class': 'formfields'}),
            'TipoConta': forms.Select(attrs={'class': 'formfields'}, choices=TIPOCONTA),
            'PIX': forms.TextInput(attrs={'class': 'formfields'}),
            'Titular': forms.TextInput(attrs={'class': 'formfields'}),
            'Documento': forms.TextInput(attrs={'class': 'formfields'}),
            'idPessoal':forms.HiddenInput()
        }
