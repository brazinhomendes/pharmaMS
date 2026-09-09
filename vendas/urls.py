from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/cancelar/', views.cancelar, name='cancelar'),
    path('api/ultimas/', views.api_ultimas_vendas, name='api_ultimas_vendas'),
    path('comissoes/', views.comissoes, name='comissoes'),
    path('comissoes/regras/', views.regras_comissao, name='regras_comissao'),
    path('comissoes/regras/nova/', views.regra_comissao_nova, name='regra_comissao_nova'),
    path('comissoes/regras/<int:pk>/editar/', views.regra_comissao_editar, name='regra_comissao_editar'),
    path('comissoes/pagar/', views.comissoes_pagar, name='comissoes_pagar'),
    path('promocoes/', views.promocoes, name='promocoes'),
    path('promocoes/nova/', views.promocao_nova, name='promocao_nova'),
    path('promocoes/<int:pk>/editar/', views.promocao_editar, name='promocao_editar'),
    path('promocoes/<int:pk>/ativar/', views.promocao_ativar, name='promocao_ativar'),
    path('api/promocoes/ativas/', views.api_promocoes_ativas, name='api_promocoes_ativas'),
    path('davs/', views.davs, name='davs'),
    path('davs/novo/', views.dav_novo, name='dav_novo'),
    path('davs/<int:pk>/', views.dav_detalhe, name='dav_detalhe'),
    path('davs/<int:pk>/editar/', views.dav_editar, name='dav_editar'),
    path('davs/<int:pk>/finalizar/', views.dav_finalizar, name='dav_finalizar'),
    path('davs/<int:pk>/cancelar/', views.dav_cancelar, name='dav_cancelar'),
    path('davs/<int:pk>/imprimir/', views.dav_imprimir, name='dav_imprimir'),
    path('api/produtos/preco/', views.api_produto_preco, name='api_produto_preco'),
]
