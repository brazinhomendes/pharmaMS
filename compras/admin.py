from django.contrib import admin
from .models import PedidoCompra, ItemPedidoCompra, NotaFiscalEntrada, SugestaoCompra, ItemSugestaoCompra


class ItemPedidoCompraInline(admin.TabularInline):
    model = ItemPedidoCompra
    extra = 1


@admin.register(PedidoCompra)
class PedidoCompraAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'fornecedor', 'data_pedido', 'status')
    list_filter = ('status', 'data_pedido')
    search_fields = ('numero_pedido', 'fornecedor__nome')
    inlines = [ItemPedidoCompraInline]


@admin.register(ItemPedidoCompra)
class ItemPedidoCompraAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade', 'preco_unitario')
    list_filter = ('pedido__status',)


class ItemSugestaoCompraInline(admin.TabularInline):
    model = ItemSugestaoCompra
    extra = 0


@admin.register(SugestaoCompra)
class SugestaoCompraAdmin(admin.ModelAdmin):
    list_display = ('data_geracao', 'data_inicio_analise', 'data_fim_analise', 'processada')
    list_filter = ('processada', 'data_geracao')
    inlines = [ItemSugestaoCompraInline]


@admin.register(ItemSugestaoCompra)
class ItemSugestaoCompraAdmin(admin.ModelAdmin):
    list_display = ('sugestao', 'produto', 'estoque_atual', 'vendas_periodo', 'dias_estoque', 'sugestao_compra', 'prioridade', 'aprovado')
    list_filter = ('prioridade', 'aprovado')


@admin.register(NotaFiscalEntrada)
class NotaFiscalEntradaAdmin(admin.ModelAdmin):
    list_display = ('numero_nf', 'fornecedor', 'data_emissao', 'valor_total', 'processada')
    list_filter = ('processada', 'data_emissao')
    search_fields = ('numero_nf', 'fornecedor__nome', 'chave_acesso')
