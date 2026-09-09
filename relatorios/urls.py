from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.index, name='index'),
    path('vendas/', views.rel_vendas, name='vendas'),
    path('vendas/json/', views.rel_vendas_json, name='vendas_json'),
    path('produtos/', views.rel_produtos, name='produtos'),
    path('produtos/json/', views.rel_produtos_json, name='produtos_json'),
    path('clientes/', views.rel_clientes, name='clientes'),
    path('clientes/json/', views.rel_clientes_json, name='clientes_json'),
    path('estoque/', views.rel_estoque, name='estoque'),
    path('financeiro/', views.rel_financeiro, name='financeiro'),
]
