from django.urls import path
from . import views

app_name = 'pdv'

urlpatterns = [
    path('', views.index, name='index'),
    path('abrir-caixa/', views.abrir_caixa, name='abrir_caixa'),
    path('fechar-caixa/', views.fechar_caixa, name='fechar_caixa'),
    path('api/finalizar-venda/', views.api_finalizar_venda, name='api_finalizar_venda'),
    path('api/buscar-produto/', views.api_buscar_produto_pdv, name='api_buscar_produto_pdv'),
    path('api/dados-caixa/', views.api_dados_caixa, name='api_dados_caixa'),
]
