from django.urls import path
from . import system_admin_views as views

app_name = 'system_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('empresas/', views.empresas_lista, name='empresas_lista'),
    path('empresa/nova/', views.empresa_nova, name='empresa_nova'),
    path('empresa/<int:pk>/editar/', views.empresa_editar, name='empresa_editar'),
    path('empresa/<int:pk>/excluir/', views.empresa_excluir, name='empresa_excluir'),
    path('usuarios/', views.usuarios_lista, name='usuarios_lista'),
    path('usuario/novo/', views.usuario_novo, name='usuario_novo'),
    path('usuario/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuario/<int:pk>/excluir/', views.usuario_excluir, name='usuario_excluir'),
    path('api/empresa/<int:empresa_id>/usuarios/', views.api_empresa_usuarios, name='api_empresa_usuarios'),
]
