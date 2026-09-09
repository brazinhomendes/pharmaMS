from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/status/', views.atualizar_status, name='atualizar_status'),
    path('api/buscar-cliente/', views.api_buscar_cliente, name='api_buscar_cliente'),
]
