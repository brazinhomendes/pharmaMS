from django.contrib import admin
from .audit_models import AuditLog, PoliticaPrivacidade, ConsentimentoLGPD, AcessoDadoSensiveis

admin.site.site_header = 'pharmaMS - Administracao'
admin.site.site_title = 'pharmaMS'
admin.site.index_title = 'Painel de Controle'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['acao', 'usuario', 'empresa', 'modelo', 'objeto_id', 'ip_address', 'timestamp']
    list_filter = ['acao', 'timestamp']
    search_fields = ['usuario__username', 'descricao', 'modelo']
    readonly_fields = ['usuario', 'empresa', 'acao', 'modelo', 'objeto_id', 'descricao',
                       'ip_address', 'user_agent', 'dados_anteriores', 'dados_novos', 'timestamp']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PoliticaPrivacidade)
class PoliticaPrivacidadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'versao', 'ativo', 'criado_em']
    list_filter = ['ativo']


@admin.register(ConsentimentoLGPD)
class ConsentimentoLGPDAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'aceito', 'timestamp']
    list_filter = ['tipo', 'aceito']


@admin.register(AcessoDadoSensiveis)
class AcessoDadoSensiveisAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_documento', 'objeto_tipo', 'objeto_id', 'timestamp']
    list_filter = ['tipo_documento']
    date_hierarchy = 'timestamp'
