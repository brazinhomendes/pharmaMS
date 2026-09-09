from django.contrib import admin
from .models import Venda, ItemVenda, FaturaVenda, RegraComissao, ComissaoVenda, Promocao, DAV, ItemDAV


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal')


class FaturaVendaInline(admin.TabularInline):
    model = FaturaVenda
    extra = 0


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('numero_venda', 'cliente', 'total', 'forma_pagamento', 'status', 'data_venda')
    list_filter = ('status', 'forma_pagamento', 'empresa')
    search_fields = ('numero_venda', 'cliente__nome')
    readonly_fields = ('data_venda', 'subtotal', 'desconto', 'total')
    inlines = [ItemVendaInline, FaturaVendaInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ('venda', 'produto', 'quantidade', 'preco_unitario', 'subtotal')
    search_fields = ('venda__numero_venda', 'produto__nome')


@admin.register(FaturaVenda)
class FaturaVendaAdmin(admin.ModelAdmin):
    list_display = ('venda', 'parcela', 'valor', 'data_vencimento', 'pago')
    list_filter = ('pago',)


@admin.register(RegraComissao)
class RegraComissaoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'percentual', 'produto', 'classe_terapeutica', 'vendedor', 'ativo')
    list_filter = ('tipo', 'ativo', 'empresa')
    search_fields = ('produto__nome', 'vendedor__nome_completo')


@admin.register(Promocao)
class PromocaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'percentual_desconto', 'data_inicio', 'data_fim', 'ativo')
    list_filter = ('tipo', 'ativo', 'empresa')
    search_fields = ('nome',)


@admin.register(ComissaoVenda)
class ComissaoVendaAdmin(admin.ModelAdmin):
    list_display = ('venda', 'vendedor', 'valor_comissao', 'paga', 'data_pagamento')
    list_filter = ('paga', 'empresa')


class ItemDAVInline(admin.TabularInline):
    model = ItemDAV
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'preco_unitario', 'desconto', 'subtotal')


@admin.register(DAV)
class DAVAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'status', 'total_geral', 'data_criacao')
    list_filter = ('status', 'empresa')
    search_fields = ('numero', 'cliente__nome')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'total_produtos', 'total_descontos', 'total_geral')
    inlines = [ItemDAVInline]


@admin.register(ItemDAV)
class ItemDAVAdmin(admin.ModelAdmin):
    list_display = ('dav', 'produto', 'quantidade', 'preco_unitario', 'subtotal')
    search_fields = ('dav__numero', 'produto__nome')
