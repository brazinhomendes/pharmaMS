from django.contrib import admin
from .models import TemplateWhatsApp, MensagemWhatsApp, EvolutionConfig, ConversaWhatsApp


@admin.register(TemplateWhatsApp)
class TemplateWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'empresa', 'ativo', 'criado_em']
    list_filter = ['categoria', 'ativo', 'empresa']
    search_fields = ['nome', 'empresa__nome']


@admin.register(MensagemWhatsApp)
class MensagemWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['destinatario_nome', 'destinatario_telefone', 'status', 'direcao', 'empresa', 'criado_em']
    list_filter = ['status', 'direcao', 'empresa']
    search_fields = ['destinatario_nome', 'destinatario_telefone', 'mensagem']
    readonly_fields = ['criado_em', 'enviado_em']
    date_hierarchy = 'criado_em'


@admin.register(EvolutionConfig)
class EvolutionConfigAdmin(admin.ModelAdmin):
    list_display = ['nome_instancia', 'api_url', 'ativo', 'auto_responder', 'empresa']
    list_filter = ['ativo', 'auto_responder', 'empresa']
    search_fields = ['nome_instancia', 'api_url']


@admin.register(ConversaWhatsApp)
class ConversaWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['telefone', 'nome', 'etapa', 'empresa', 'ultimo_mensagem_em']
    list_filter = ['etapa', 'empresa']
    search_fields = ['telefone', 'nome']
