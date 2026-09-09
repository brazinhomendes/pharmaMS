from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('template/novo/', views.template_novo, name='template_novo'),
    path('template/<int:pk>/editar/', views.template_editar, name='template_editar'),
    path('template/<int:pk>/excluir/', views.template_excluir, name='template_excluir'),
    path('enviar/', views.enviar_mensagem, name='enviar'),
    path('api/status/', views.api_status_mensagens, name='api_status'),
    path('evolution/', views.evolution_config, name='evolution_config'),
    path('evolution/<int:pk>/conectar/', views.evolution_conectar, name='evolution_conectar'),
    path('evolution/<int:pk>/qrcode/', views.evolution_qrcode, name='evolution_qrcode'),
    path('evolution/<int:pk>/webhook/', views.evolution_configurar_webhook, name='evolution_webhook'),
    path('webhook/', views.webhook_evolution, name='webhook'),
]
