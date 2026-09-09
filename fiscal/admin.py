from django.contrib import admin
from .models import CFOP, NCM, NFe, NFCe, ConfiguracaoFiscal, SpedContribuicoes, Sintegra


@admin.register(CFOP)
class CFOPAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descricao', 'aplicacao', 'ativo']
    search_fields = ['codigo', 'descricao']


@admin.register(NCM)
class NCMAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descricao', 'ativo']
    search_fields = ['codigo', 'descricao']


@admin.register(NFe)
class NFeAdmin(admin.ModelAdmin):
    list_display = ['serie', 'numero', 'modelo', 'cliente', 'valor_total', 'status', 'empresa']
    list_filter = ['status', 'modelo', 'empresa']
    search_fields = ['numero', 'chave_acesso']


@admin.register(ConfiguracaoFiscal)
class ConfiguracaoFiscalAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'serie_nfe', 'serie_nfce', 'regime_tributario']
    list_filter = ['empresa']


@admin.register(SpedContribuicoes)
class SpedContribuicoesAdmin(admin.ModelAdmin):
    list_display = ['periodo', 'tipo_contribuicao', 'processado', 'empresa']
    list_filter = ['processado', 'empresa']


@admin.register(Sintegra)
class SintegraAdmin(admin.ModelAdmin):
    list_display = ['periodo', 'processado', 'empresa']
    list_filter = ['processado', 'empresa']


@admin.register(NFCe)
class NFCeAdmin(admin.ModelAdmin):
    list_display = ['numero', 'serie', 'venda', 'chave_acesso', 'tipo_emissao', 'status_autorizacao', 'empresa']
    list_filter = ['status_autorizacao', 'tipo_emissao', 'empresa']
    search_fields = ['numero', 'chave_acesso']
