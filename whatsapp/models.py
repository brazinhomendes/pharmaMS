from django.db import models
from django.utils import timezone
from core.models import BaseEmpresa


class EvolutionConfig(BaseEmpresa):
    nome_instancia = models.CharField(max_length=100, help_text='Nome da instancia no Evolution API')
    api_url = models.URLField(help_text='URL base do Evolution API (ex: http://localhost:8080)')
    api_key = models.CharField(max_length=255, help_text='API Key do Evolution API')
    webhook_url = models.URLField(blank=True, default='', help_text='URL do webhook (preenchido automaticamente)')
    ativo = models.BooleanField(default=True)
    auto_responder = models.BooleanField(default=True, help_text='Ativar agente automatico para responder mensagens')
    mensagem_boas_vindas = models.TextField(
        default='Ola! Bem-vindo a {empresa}! Como posso ajudar?\n\n'
                '1 - Ver promocoes\n'
                '2 - Consultar pedido\n'
                '3 - Falar com atendente\n'
                '4 - Horario de funcionamento',
        help_text='Mensagem enviada quando o cliente envia a primeira mensagem'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Configuracao Evolution API'
        verbose_name_plural = 'Configuracoes Evolution API'

    def __str__(self):
        return f'{self.nome_instancia} ({self.api_url})'


class TemplateWhatsApp(BaseEmpresa):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, choices=[
        ('pedido_confirmado', 'Pedido Confirmado'),
        ('pedido_enviado', 'Pedido Enviado'),
        ('pedido_entregue', 'Pedido Entregue'),
        ('promocao', 'Promocao'),
        ('lembrete', 'Lembretes'),
        ('nfe', 'Envio de NF-e'),
        ('personalizado', 'Personalizado'),
    ])
    corpo = models.TextField(help_text='Use {variavel} para campos dinamicos')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Template WhatsApp'
        verbose_name_plural = 'Templates WhatsApp'

    def __str__(self):
        return f'{self.nome} ({self.get_categoria_display()})'


class ConversaWhatsApp(BaseEmpresa):
    telefone = models.CharField(max_length=20)
    nome = models.CharField(max_length=200, blank=True, default='')
    etapa = models.CharField(max_length=50, default='inicio', choices=[
        ('inicio', 'Inicio'),
        ('menu_principal', 'Menu Principal'),
        ('aguardando_pedido', 'Aguardando Numero do Pedido'),
        ('aguardando_atendente', 'Aguardando Atendente'),
        ('conversa_ativa', 'Conversa Ativa'),
    ])
    ultimo_mensagem_em = models.DateTimeField(auto_now=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ultimo_mensagem_em']
        verbose_name = 'Conversa WhatsApp'
        verbose_name_plural = 'Conversas WhatsApp'

    def __str__(self):
        return f'{self.telefone} - {self.nome} ({self.get_etapa_display()})'


class MensagemWhatsApp(BaseEmpresa):
    TEMPLATE_STATUS = [
        ('pendente', 'Pendente'),
        ('enviada', 'Enviada'),
        ('entregue', 'Entregue'),
        ('lida', 'Lida'),
        ('erro', 'Erro'),
        ('recebida', 'Recebida'),
    ]

    conversa = models.ForeignKey(ConversaWhatsApp, on_delete=models.CASCADE, null=True, blank=True)
    template = models.ForeignKey(TemplateWhatsApp, on_delete=models.SET_NULL, null=True, blank=True)
    destinatario_nome = models.CharField(max_length=200, blank=True, default='')
    destinatario_telefone = models.CharField(max_length=20)
    mensagem = models.TextField()
    mensagem_id = models.CharField(max_length=100, blank=True, default='', help_text='ID da mensagem no Evolution API')
    direcao = models.CharField(max_length=10, default='enviada', choices=[
        ('enviada', 'Enviada'),
        ('recebida', 'Recebida'),
    ])
    status = models.CharField(max_length=20, choices=TEMPLATE_STATUS, default='pendente')
    erro_detalhes = models.TextField(blank=True, default='')
    enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'

    def __str__(self):
        return f'{self.destinatario_nome} -> {self.status}'
