from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('liberacoes/', views.liberacoes, name='liberacoes'),
    path('liberacoes/solicitar/', views.liberacao_solicitar, name='liberacao_solicitar'),
    path('liberacoes/<int:pk>/aprovar/', views.liberacao_aprovar, name='liberacao_aprovar'),
    path('liberacoes/<int:pk>/rejeitar/', views.liberacao_rejeitar, name='liberacao_rejeitar'),
    path('liberacoes/pendentes/', views.liberacoes_pendentes, name='liberacoes_pendentes'),
    path('cancelamentos/', views.cancelamentos, name='cancelamentos'),
]
