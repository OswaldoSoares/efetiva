from django.urls import path
from .views import index_minuta, criaminuta, editaminuta, imprimeminuta, conclui_minuta, fecha_minuta, estorna_minuta,\
    consultaminuta, criaminutamotorista, excluiminutamotorista, criaminutaajudante, excluiminutaajudante,\
    editaminutaveiculo, editaminutakminicial, editaminutakmfinal, editaminutahorafinal, criaminutadespesa,\
    excluiminutadespesa, criaminutaparametrodespesa, criaminutaentrega, editaminutaentrega, excluiminutaentrega,\
    filtraminutaveiculo, buscaminutaentrega, edita_comentario, exclui_minuta, edita_minuta_saida_extra_ajudante, \
    edita_minuta_km_final


urlpatterns = [
    path('', index_minuta, name='index_minuta'),
    path('criaminuta', criaminuta, name='criaminuta'),
    path('editaminuta/<int:idmin>/', editaminuta, name='editaminuta'),
    path('imprimeminuta/<int:idmin>/', imprimeminuta, name='imprimeminuta'),
    path('concluiminuta/<int:idmin>/', conclui_minuta, name='concluiminuta'),
    path('fecha_minuta/<int:idmin>/', fecha_minuta, name='fecha_minuta'),
    path('estorna_minuta/<int:idmin>/', estorna_minuta, name='estorna_minuta'),
    path('consultaminuta/<int:idmin>/', consultaminuta, name='consultaminuta'),
    path('criaminutamotorista/', criaminutamotorista, name='criaminutamotorista'),
    path('excluiminutamotorista/<int:idmincol>/', excluiminutamotorista, name='excluiminutamotorista'),
    path('criaminutaajudante/', criaminutaajudante, name='criaminutaajudante'),
    path('excluiminutaajudante/<int:idmincol>/', excluiminutaajudante, name='excluiminutaajudante'),
    path('editaminutaveiculo/<int:idmin>/', editaminutaveiculo, name='editaminutaveiculo'),
    path('editaminutakminicial/<int:idmin>/', editaminutakminicial, name='editaminutakminicial'),
    path('editaminutakmfinal/<int:idmin>/', editaminutakmfinal, name='editaminutakmfinal'),
    path('editaminutahorafinal/<int:idmin>/', editaminutahorafinal, name='editaminutahorafinal'),
    path('criaminutadespesa', criaminutadespesa, name='criaminutadespesa'),
    path('excluiminutadespesa/<int:idmindes>/', excluiminutadespesa, name='excluiminutadespesa'),
    path('criaminutaparametrodespesa', criaminutaparametrodespesa, name='criaminutaparametrodespesa'),
    path('criaminutaentrega', criaminutaentrega, name='criaminutaentrega'),
    path('editaminutaentrega/<int:idminent>/', editaminutaentrega, name='editaminutaentrega'),
    path('excluiminutaentrega/<int:idminent>/', excluiminutaentrega, name='excluiminutaentrega'),
    path('buscaminutaentrega/', buscaminutaentrega, name='buscaminutaentrega'),
    path('editacomentario/<int:idmin>/', edita_comentario, name='editacomentario'),
    path('filtraminutaveiculo/', filtraminutaveiculo, name='filtraminutaveiculo'),
    path('excluiminuta/<int:idminuta>/', exclui_minuta, name='excluiminuta'),
    path('editaminutasaidaextraajudante/<int:idminuta>', edita_minuta_saida_extra_ajudante,
         name='editaminutasaidaextraajudante'),
    path('editakmfinal/', edita_minuta_km_final, name='editakmfinal'),
]