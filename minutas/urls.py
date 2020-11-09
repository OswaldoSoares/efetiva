from django.urls import path
from .views import index_minuta,\
    criaminuta,\
    editaminuta,\
    imprimeminuta,\
    fecha_minuta,\
    estorna_minuta,\
    consultaminuta,\
    criaminutamotorista,\
    excluiminutamotorista,\
    criaminutaajudante,\
    excluiminutaajudante,\
    editaminutaveiculo,\
    editaminutakminicial,\
    editaminutakmfinal,\
    editaminutahorafinal,\
    criaminutadespesa,\
    excluiminutadespesa,\
    criaminutaparametrodespesa,\
    criaminutaentrega,\
    editaminutaentrega,\
    excluiminutaentrega,\
    filtraminutaveiculo

urlpatterns = [
    path(
        '',
        index_minuta,
        name='index_minuta'
    ),
    path(
        'criaminuta',
        criaminuta,
        name='criaminuta'
    ),
    path(
        'editaminuta/<int:idmin>/',
        editaminuta,
        name='editaminuta'
    ),
    path(
        'imprimeminuta/<int:idmin>/',
        imprimeminuta,
        name='imprimeminuta'
    ),
    path(
        'fecha_minuta/<int:idmin>/',
        fecha_minuta,
        name='fecha_minuta'
    ),
    path(
        'estorna_minuta/<int:idmin>/',
        estorna_minuta,
        name='estorna_minuta'
    ),
    path(
        'consultaminuta/<int:idmin>/',
        consultaminuta,
        name='consultaminuta'
    ),
    path(
        'criaminutamotorista/',
        criaminutamotorista,
        name='criaminutamotorista'
    ),
    path(
        'excluiminutamotorista/<int:idmincol>/',
        excluiminutamotorista,
        name='excluiminutamotorista'
    ),
    path(
        'criaminutaajudante/',
        criaminutaajudante,
        name='criaminutaajudante'
    ),
    path(
        'excluiminutaajudante/<int:idmincol>/',
        excluiminutaajudante,
        name='excluiminutaajudante'
    ),
    path(
        'editaminutaveiculo/<int:idmin>/',
         editaminutaveiculo,
         name='editaminutaveiculo'
    ),
    path(
        'editaminutakminicial/<int:idmin>/',
        editaminutakminicial,
        name='editaminutakminicial'
    ),
    path(
        'editaminutakmfinal/<int:idmin>/',
        editaminutakmfinal,
        name='editaminutakmfinal'
    ),
    path(
        'editaminutahorafinal/<int:idmin>/',
        editaminutahorafinal,
        name='editaminutahorafinal'
    ),
    path(
        'criaminutadespesa',
        criaminutadespesa,
        name='criaminutadespesa'
    ),
    path(
        'excluiminutadespesa/<int:idmindes>/',
        excluiminutadespesa,
        name='excluiminutadespesa'
    ),
    path(
        'criaminutaparametrodespesa',
        criaminutaparametrodespesa,
        name='criaminutaparametrodespesa'
    ),
    path(
        'criaminutaentrega',
        criaminutaentrega,
        name='criaminutaentrega'
    ),
    path(
        'editaminutaentrega/<int:idminent>/',
        editaminutaentrega,
        name='editaminutaentrega'
    ),
    path(
        'excluiminutaentrega/<int:idminent>/',
        excluiminutaentrega,
        name='excluiminutaentrega'
    ),
    path(
        'filtraminutaveiculo/',
        filtraminutaveiculo,
        name='filtraminutaveiculo'
    )
]