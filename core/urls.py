from django.urls import path
from . import views
from .onboarding_views import onboarding, onboarding_empresa
from .landing_view import landing

app_name = 'core'

urlpatterns = [
    path('', landing, name='landing'),
    path('app/', views.dashboard, name='dashboard'),
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
    path('onboarding/', onboarding, name='onboarding'),
    path('onboarding/empresa/', onboarding_empresa, name='onboarding_empresa'),
]
