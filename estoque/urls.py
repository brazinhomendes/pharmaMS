from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.index, name='index'),
    path('lotes/', views.lotes, name='lotes'),
    path('lotes/novo/', views.lote_novo, name='lote_novo'),
    path('movimentos/', views.movimentos, name='movimentos'),
    path('api/produto/<int:pk>/lotes/', views.api_lotes_produto, name='api_lotes_produto'),
]
