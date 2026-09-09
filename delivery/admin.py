from django.contrib import admin
from .models import Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'status', 'entregador', 'data_entrega', 'taxa_entrega', 'empresa']
    list_filter = ['status', 'data_entrega']
    search_fields = ['cliente__nome', 'endereco_entrega', 'bairro']
    raw_id_fields = ['venda', 'cliente', 'entregador']
    readonly_fields = [
        'status_pendente_em', 'status_atribuido_em',
        'status_em_rota_em', 'status_entregue_em', 'status_cancelada_em'
    ]
