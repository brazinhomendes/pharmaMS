from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACOES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Criar'),
        ('read', 'Consultar'),
        ('update', 'Atualizar'),
        ('delete', 'Excluir'),
        ('export', 'Exportar'),
        ('approve', 'Aprovar'),
        ('reject', 'Rejeitar'),
        ('cancel', 'Cancelar'),
        ('emit_nfe', 'Emitir NF-e'),
        ('emit_nfce', 'Emitir NFC-e'),
        ('open_cash', 'Abrir Caixa'),
        ('close_cash', 'Fechar Caixa'),
        ('sale', 'Venda'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs'
    )
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    acao = models.CharField(max_length=20, choices=ACOES)
    modelo = models.CharField(max_length=100, blank=True, default='')
    objeto_id = models.CharField(max_length=50, blank=True, default='')
    descricao = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    dados_anteriores = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['empresa', '-timestamp']),
            models.Index(fields=['acao', '-timestamp']),
        ]
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'

    def __str__(self):
        user = self.usuario.username if self.usuario else 'anon'
        return f'[{self.acao}] {user} - {self.modelo} {self.objeto_id} - {self.timestamp:%d/%m/%Y %H:%M}'


class PoliticaPrivacidade(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    versao = models.CharField(max_length=10, default='1.0')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Politica de Privacidade'
        verbose_name_plural = 'Politicas de Privacidade'

    def __str__(self):
        return f'{self.titulo} v{self.versao}'


class ConsentimentoLGPD(models.Model):
    TIPO_CHOICES = [
        ('termos', 'Termos de Uso'),
        ('privacidade', 'Politica de Privacidade'),
        ('marketing', 'Comunicacoes de Marketing'),
        ('cookies', 'Cookies'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consentimentos'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    aceito = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    revogado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['usuario', 'tipo']
        ordering = ['-timestamp']
        verbose_name = 'Consentimento LGPD'
        verbose_name_plural = 'Consentimentos LGPD'

    def __str__(self):
        status = 'Aceito' if self.aceito else 'Recusado'
        return f'{self.usuario} - {self.get_tipo_display()} - {status}'


class AcessoDadoSensiveis(models.Model):
    TIPO_DOCUMENTO = [
        ('cpf', 'CPF'),
        ('cnpj', 'CNPJ'),
        ('rg', 'RG'),
        ('receita', 'Receita Medica'),
        ('outro', 'Outro'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='acessos_dados_sensiveis'
    )
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO)
    objeto_tipo = models.CharField(max_length=100)
    objeto_id = models.CharField(max_length=50)
    motivo = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Acesso a Dado Sensivel'
        verbose_name_plural = 'Acessos a Dados Sensiveis'

    def __str__(self):
        return f'{self.usuario} acessou {self.tipo_documento} em {self.objeto_tipo}#{self.objeto_id}'
