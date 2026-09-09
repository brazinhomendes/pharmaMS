from django.contrib import admin
from .models import OperadoraPBM, TransacaoPBM, ItemTransacaoPBM


@admin.register(OperadoraPBM)
class OperadoraPBMAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome']


class ItemTransacaoPBMInline(admin.TabularInline):
    model = ItemTransacaoPBM
    extra = 1


@admin.register(TransacaoPBM)
class TransacaoPBMAdmin(admin.ModelAdmin):
    list_display = ['operadora', 'venda', 'status', 'valor_total', 'empresa']
    list_filter = ['status', 'operadora', 'empresa']
    inlines = [ItemTransacaoPBMInline]


@admin.register(ItemTransacaoPBM)
class ItemTransacaoPBMAdmin(admin.ModelAdmin):
    list_display = ['transacao', 'produto', 'quantidade', 'valor_unitario', 'valor_aprovado']
