from django.urls import path
from . import views

app_name = 'configuracoes'

urlpatterns = [
    path('', views.index, name='index'),
    path('fiscal/', views.fiscal, name='fiscal'),
    path('municipal/', views.municipal, name='municipal'),
    path('email/', views.email_config, name='email'),
    path('backup/', views.backup_config, name='backup'),
]
