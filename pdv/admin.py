from django.contrib import admin
from .models import Caixa, MovimentoCaixa


class MovimentoCaixaInline(admin.TabularInline):
    model = MovimentoCaixa
    extra = 0
    readonly_fields = ('tipo', 'valor', 'descricao', 'venda', 'usuario')


@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario_abertura', 'data_abertura', 'status', 'saldo_inicial', 'saldo_final')
    list_filter = ('status', 'empresa')
    readonly_fields = ('data_abertura',)
    inlines = [MovimentoCaixaInline]


@admin.register(MovimentoCaixa)
class MovimentoCaixaAdmin(admin.ModelAdmin):
    list_display = ('caixa', 'tipo', 'valor', 'descricao', 'usuario', 'criado_em')
    list_filter = ('tipo',)
