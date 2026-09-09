from django.db import models
from core.models import BaseEmpresa, BaseModel


class CFOP(BaseModel):
    codigo = models.CharField(max_length=10, unique=True)
    descricao = models.CharField(max_length=200)
    aplicacao = models.CharField(
        max_length=1, blank=True,
        help_text='1-Entrada 2-Saida'
    )

    def __str__(self):
        return f'{self.codigo} - {self.descricao}'

    class Meta:
        ordering = ['codigo']


class NCM(BaseModel):
    codigo = models.CharField(max_length=10, unique=True)
    descricao = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.codigo} - {self.descricao}'


class NFe(BaseEmpresa):
    MOD_CHOICES = (('55', 'NF-e'), ('65', 'NFC-e'))
    modelo = models.CharField(max_length=2, default='55', choices=MOD_CHOICES)
    serie = models.IntegerField(default=1)
    numero = models.IntegerField()
    chave_acesso = models.CharField(max_length=50, blank=True)
    cliente = models.ForeignKey(
        'cadastros.Cliente', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    venda = models.ForeignKey(
        'vendas.Venda', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    data_emissao = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pendente', 'Pendente'),
            ('autorizada', 'Autorizada'),
            ('rejeitada', 'Rejeitada'),
            ('cancelada', 'Cancelada'),
            ('denegada', 'Denegada'),
        ),
        default='pendente'
    )
    protocolo = models.CharField(max_length=50, blank=True)
    xml_enviado = models.TextField(blank=True)
    xml_retorno = models.TextField(blank=True)
    data_autorizacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'NFe {self.serie}-{self.numero}'

    class Meta:
        verbose_name = 'NF-e/NFC-e'
        ordering = ['-criado_em']


class ConfiguracaoFiscal(BaseEmpresa):
    serie_nfe = models.IntegerField(default=1)
    serie_nfce = models.IntegerField(default=1)
    proximo_numero_nfe = models.IntegerField(default=1)
    proximo_numero_nfce = models.IntegerField(default=1)
    regime_tributario = models.CharField(
        max_length=1,
        choices=(
            ('1', 'Simples Nacional'),
            ('2', 'Simples Excesso'),
            ('3', 'Regime Normal'),
        ),
        default='1'
    )
    certificado_digital = models.FileField(
        upload_to='fiscal/certificados/', blank=True
    )
    senha_certificado = models.CharField(max_length=100, blank=True)
    csc = models.CharField(max_length=100, blank=True)
    csc_id = models.CharField(max_length=10, blank=True)
    token_ibpt = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'Config Fiscal - {self.empresa}'


class SpedContribuicoes(BaseEmpresa):
    periodo = models.CharField(
        max_length=7, help_text='MM/AAAA'
    )
    tipo_contribuicao = models.CharField(
        max_length=10,
        choices=(
            ('mensal', 'Mensal'),
            ('trimestral', 'Trimestral'),
        ),
        default='mensal'
    )
    arquivo_gerado = models.FileField(
        upload_to='fiscal/sped/', blank=True
    )
    processado = models.BooleanField(default=False)

    def __str__(self):
        return f'SPED {self.periodo}'


class Sintegra(BaseEmpresa):
    periodo = models.CharField(
        max_length=7, help_text='MM/AAAA'
    )
    arquivo_gerado = models.FileField(
        upload_to='fiscal/sintegra/', blank=True
    )
    processado = models.BooleanField(default=False)

    def __str__(self):
        return f'Sintegra {self.periodo}'


class NFCe(BaseEmpresa):
    MODELO_CHOICES = [('65', 'NFC-e (65)')]
    TIPO_EMISSAO_CHOICES = [
        ('1', 'Normal'),
        ('2', 'Contingencia'),
    ]
    STATUS_AUTORIZACAO_CHOICES = [
        ('pendente', 'Pendente'),
        ('autorizada', 'Autorizada'),
        ('denegada', 'Denegada'),
        ('cancelada', 'Cancelada'),
    ]

    venda = models.ForeignKey(
        'vendas.Venda', on_delete=models.CASCADE,
        related_name='nfces'
    )
    numero = models.CharField(max_length=20)
    serie = models.IntegerField(default=1)
    chave_acesso = models.CharField(max_length=44, unique=True)
    modelo = models.CharField(
        max_length=2, choices=MODELO_CHOICES, default='65'
    )
    tipo_emissao = models.CharField(
        max_length=1, choices=TIPO_EMISSAO_CHOICES, default='1'
    )
    status_autorizacao = models.CharField(
        max_length=10, choices=STATUS_AUTORIZACAO_CHOICES,
        default='pendente'
    )
    xml_enviado = models.TextField(blank=True)
    xml_retorno = models.TextField(blank=True)
    protocolo = models.CharField(max_length=20, blank=True)
    numero_lote = models.CharField(max_length=20, blank=True)
    data_autorizacao = models.DateTimeField(null=True, blank=True)
    data_emissao = models.DateTimeField(auto_now_add=True)
    justificativa_contingencia = models.TextField(blank=True)

    def __str__(self):
        return f'NFC-e {self.numero} - {self.status_autorizacao}'

    class Meta:
        verbose_name = 'NFC-e'
        verbose_name_plural = 'NFC-e'
        ordering = ['-criado_em']
