from django.contrib import admin
from .models import ClasseTerapeutica, Laboratorio, Produto, Cliente, Fornecedor, ModeloEtiqueta, ImpressaoEtiqueta, ItemImpressaoEtiqueta


@admin.register(ClasseTerapeutica)
class ClasseTerapeuticaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    search_fields = ['nome']


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'ativo']
    search_fields = ['nome', 'cnpj']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_barras', 'preco_venda', 'laboratorio', 'ativo']
    search_fields = ['nome', 'codigo_barras']
    list_filter = ['ativo', 'laboratorio', 'classe_terapeutica']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'cidade', 'telefone', 'ativo']
    search_fields = ['nome', 'cpf_cnpj', 'email']
    list_filter = ['ativo', 'cidade']


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'cidade', 'telefone', 'ativo']
    search_fields = ['nome', 'cnpj']
    list_filter = ['ativo', 'cidade']


@admin.register(ModeloEtiqueta)
class ModeloEtiquetaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'largura_mm', 'altura_mm', 'colunas', 'linhas', 'ativo']
    search_fields = ['nome']


@admin.register(ImpressaoEtiqueta)
class ImpressaoEtiquetaAdmin(admin.ModelAdmin):
    list_display = ['modelo', 'tipo_origem', 'data_impressao', 'usuario', 'empresa']
    list_filter = ['modelo', 'tipo_origem', 'data_impressao']


@admin.register(ItemImpressaoEtiqueta)
class ItemImpressaoEtiquetaAdmin(admin.ModelAdmin):
    list_display = ['impressao', 'produto', 'lote', 'quantidade']
