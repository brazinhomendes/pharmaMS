from django.urls import path
from . import views

app_name = 'pbm'

urlpatterns = [
    path('', views.index, name='index'),
    path('transacoes/', views.transacoes, name='transacoes'),
    path('transacao/nova/', views.transacao_nova, name='transacao_nova'),
    path('transacao/<int:pk>/', views.transacao_detalhe, name='transacao_detalhe'),
    path('transacao/<int:pk>/status/', views.transacao_atualizar_status, name='transacao_atualizar_status'),
    path('operadora/nova/', views.operadora_nova, name='operadora_nova'),
    path('api/resumo/', views.api_transacoes_resumo, name='api_resumo'),
]
