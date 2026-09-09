from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/receber/', views.receber, name='receber'),
    path('nfs/', views.nf_entrada_lista, name='nf_entrada_lista'),
    path('sugestoes/', views.sugestoes, name='sugestoes'),
    path('sugestoes/gerar/', views.sugestoes_gerar, name='sugestoes_gerar'),
    path('sugestoes/<int:pk>/', views.sugestao_detalhe, name='sugestao_detalhe'),
    path('sugestoes/<int:pk>/criar-pedido/', views.sugestao_criar_pedido, name='sugestao_criar_pedido'),
    path('sugestoes/<int:pk>/aprovar-item/<int:item_pk>/', views.sugestao_aprovar_item, name='sugestao_aprovar_item'),
]
