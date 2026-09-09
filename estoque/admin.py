from django.contrib import admin
from .models import Lote, MovimentoEstoque


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('codigo_lote', 'produto', 'quantidade', 'data_validade', 'preco_custo')
    list_filter = ('data_validade', 'ativo')
    search_fields = ('codigo_lote', 'produto__nome')


@admin.register(MovimentoEstoque)
class MovimentoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'produto', 'quantidade', 'saldo_anterior', 'saldo_posterior', 'criado_em')
    list_filter = ('tipo',)
    search_fields = ('produto__nome', 'documento')
