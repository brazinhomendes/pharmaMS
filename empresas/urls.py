from django.urls import path
from . import views

app_name = 'empresas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nova/', views.nova, name='nova'),
    path('<int:pk>/editar/', views.editar, name='editar'),
]
