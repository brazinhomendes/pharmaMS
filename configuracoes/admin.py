from django.contrib import admin
from .models import (
    ConfiguracaoSistema, ConfigFiscalSistema,
    ConfiguracaoMunicipal, ConfiguracaoEmail, ConfiguracaoBackup
)


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'nome_sistema', 'moeda', 'tema_escuro']
    list_filter = ['moeda', 'tema_escuro']
    search_fields = ['empresa__nome', 'nome_sistema']


@admin.register(ConfigFiscalSistema)
class ConfigFiscalSistemaAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'nfe_ambiente', 'nfce_ambiente', 'nfe_serie', 'nfce_serie']
    list_filter = ['nfe_ambiente', 'nfce_ambiente', 'sped_fiscal', 'sintegra']
    search_fields = ['empresa__nome', 'cnae', 'cnes']
    fieldsets = (
        ('Empresa', {'fields': ('empresa',)}),
        ('Certificado A1', {'fields': ('certificado_a1', 'certificado_senha', 'certificado_validade')}),
        ('Dados Contribuinte', {'fields': ('cnae', 'cnes', 'codigo_municipio', 'inscricao_municipal', 'perfil_ecf')}),
        ('NF-e', {'fields': ('nfe_ambiente', 'nfe_versao', 'nfe_serie', 'nfe_numero_atual')}),
        ('NFC-e', {'fields': ('nfce_ambiente', 'nfce_versao', 'nfce_serie', 'nfce_numero_atual', 'nfce_csc_id', 'nfce_csc_token')}),
        ('SPED / Sintegra', {'fields': ('sped_fiscal', 'sped_contabil', 'sped_contribuicoes', 'sintegra')}),
    )


@admin.register(ConfiguracaoMunicipal)
class ConfiguracaoMunicipalAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'aliquota_icms_padrao', 'regime_tributario']
    list_filter = ['regime_tributario']
    search_fields = ['empresa__nome']


@admin.register(ConfiguracaoEmail)
class ConfiguracaoEmailAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'smtp_host', 'smtp_port', 'email_remetente']
    search_fields = ['empresa__nome', 'smtp_host']


@admin.register(ConfiguracaoBackup)
class ConfiguracaoBackupAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'backup_automatico', 'backup_frequencia', 'ultimo_backup']
    list_filter = ['backup_automatico', 'backup_frequencia']
