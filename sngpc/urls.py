from django.urls import path
from . import views

app_name = 'sngpc'

urlpatterns = [
    path('', views.index, name='index'),
    path('controlados/', views.controlados, name='controlados'),
    path('receitas/', views.receitas, name='receitas'),
    path('receitas/nova/', views.receita_nova, name='receita_nova'),
    path('movimentos/', views.movimentos, name='movimentos'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/gerar/', views.gerar_relatorio, name='gerar_relatorio'),
]
