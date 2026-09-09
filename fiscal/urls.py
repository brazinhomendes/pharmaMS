from django.urls import path
from . import views

app_name = 'fiscal'

urlpatterns = [
    path('', views.index, name='index'),
    path('nfe/', views.nfe_lista, name='nfe_lista'),
    path('nfe/nova/', views.nfe_nova, name='nfe_nova'),
    path('nfe/<int:pk>/xml/', views.nfe_xml, name='nfe_xml'),
    path('nfe/<int:pk>/cancelar/', views.nfe_cancelar, name='nfe_cancelar'),
    path('nfce/', views.nfce_lista, name='nfce_lista'),
    path('nfce/pendentes/', views.nfce_pendentes, name='nfce_pendentes'),
    path('nfce/<int:pk>/', views.nfce_detalhe, name='nfce_detalhe'),
    path('nfce/<int:pk>/xml/', views.nfce_xml, name='nfce_xml'),
    path('nfce/<int:pk>/danfe/', views.nfce_danfe, name='nfce_danfe'),
    path('nfce/<int:pk>/cancelar/', views.nfce_cancelar, name='nfce_cancelar'),
    path('nfce/reemitir-pendentes/', views.nfce_reemitir, name='nfce_reemitir'),
    path('config/', views.config, name='config'),
    path('sped/', views.sped_lista, name='sped_lista'),
    path('sintegra/', views.sintegra_lista, name='sintegra_lista'),
]
