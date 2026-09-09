from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sistema/', include('usuarios.system_admin_urls', namespace='system_admin')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', include('core.urls', namespace='core')),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('empresas/', include('empresas.urls', namespace='empresas')),
    path('cadastros/', include('cadastros.urls', namespace='cadastros')),
    path('estoque/', include('estoque.urls', namespace='estoque')),
    path('compras/', include('compras.urls', namespace='compras')),
    path('pdv/', include('pdv.urls', namespace='pdv')),
    path('vendas/', include('vendas.urls', namespace='vendas')),
    path('financeiro/', include('financeiro.urls', namespace='financeiro')),
    path('fiscal/', include('fiscal.urls', namespace='fiscal')),
    path('sngpc/', include('sngpc.urls', namespace='sngpc')),
    path('pbm/', include('pbm.urls', namespace='pbm')),
    path('crm/', include('crm.urls', namespace='crm')),
    path('delivery/', include('delivery.urls', namespace='delivery')),
    path('whatsapp/', include('whatsapp.urls', namespace='whatsapp')),
    path('relatorios/', include('relatorios.urls', namespace='relatorios')),
    path('configuracoes/', include('configuracoes.urls', namespace='configuracoes')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
