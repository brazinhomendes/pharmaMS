from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('', views.index, name='index'),
    path('contas-pagar/', views.contas_pagar, name='contas_pagar'),
    path('contas-pagar/<int:pk>/editar/', views.conta_pagar_editar, name='conta_pagar_editar'),
    path('contas-receber/', views.contas_receber, name='contas_receber'),
    path('contas-receber/<int:pk>/editar/', views.conta_receber_editar, name='conta_receber_editar'),
    path('lancamentos/', views.lancamentos, name='lancamentos'),
    path('lancamento/novo/', views.lancamento_novo, name='lancamento_novo'),
]
