from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<int:pk>/ler/', views.marcar_lida, name='marcar_lida'),
]
