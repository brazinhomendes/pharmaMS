from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.index, name='index'),
    path('campanha/nova/', views.campanha_nova, name='campanha_nova'),
    path('campanha/<int:pk>/editar/', views.campanha_editar, name='campanha_editar'),
    path('campanha/<int:pk>/excluir/', views.campanha_excluir, name='campanha_excluir'),
    path('cliente/<int:cliente_pk>/', views.cliente_crm, name='cliente_crm'),
    path('api/aniversariantes/', views.api_aniversariantes, name='api_aniversariantes'),
]
