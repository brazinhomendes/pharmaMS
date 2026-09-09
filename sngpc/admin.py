from django.contrib import admin
from .models import (
    ClasseTerapeuticaSNGPC, MedicamentoControlado, ProfissionalSaude,
    Receituario, ItemReceituario, MovimentacaoSNGPC, RelatorioSNGPC,
)


@admin.register(ClasseTerapeuticaSNGPC)
class ClasseTerapeuticaSNGPCAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'ativo']
    search_fields = ['codigo', 'nome']


@admin.register(MedicamentoControlado)
class MedicamentoControladoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'classe_terapeutica', 'tipo_receita', 'empresa']
    list_filter = ['tipo_receita', 'empresa']
    search_fields = ['produto__nome']


@admin.register(ProfissionalSaude)
class ProfissionalSaudeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'conselho', 'numero_conselho', 'uf_conselho', 'ativo']
    search_fields = ['nome', 'numero_conselho']


class ItemReceituarioInline(admin.TabularInline):
    model = ItemReceituario
    extra = 1


@admin.register(Receituario)
class ReceituarioAdmin(admin.ModelAdmin):
    list_display = ['numero_receita', 'paciente_nome', 'profissional', 'data_emissao', 'empresa']
    list_filter = ['empresa']
    search_fields = ['numero_receita', 'paciente_nome']
    inlines = [ItemReceituarioInline]


@admin.register(ItemReceituario)
class ItemReceituarioAdmin(admin.ModelAdmin):
    list_display = ['receituario', 'medicamento', 'quantidade']


@admin.register(MovimentacaoSNGPC)
class MovimentacaoSNGPCAdmin(admin.ModelAdmin):
    list_display = ['medicamento', 'tipo', 'quantidade', 'data_movimento', 'empresa']
    list_filter = ['tipo', 'empresa']


@admin.register(RelatorioSNGPC)
class RelatorioSNGPCAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'periodo_inicio', 'periodo_fim', 'processado', 'empresa']
    list_filter = ['tipo', 'processado', 'empresa']
