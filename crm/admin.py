from django.contrib import admin
from .models import Campanha, ClienteCRM


@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_inicio', 'data_fim', 'ativo', 'empresa']
    list_filter = ['ativo', 'data_inicio']
    search_fields = ['nome']


@admin.register(ClienteCRM)
class ClienteCRMAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'ultima_compra', 'total_gasto', 'empresa']
    search_fields = ['cliente__nome']
    list_filter = ['empresa']
