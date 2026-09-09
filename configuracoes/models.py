import os
from django.db import models
from core.models import BaseEmpresa


class ConfiguracaoSistema(BaseEmpresa):
    nome_sistema = models.CharField(max_length=200, default='pharmaMS')
    cor_primaria = models.CharField(max_length=7, default='#7c3aed')
    cor_secundaria = models.CharField(max_length=7, default='#1c1917')
    tema_escuro = models.BooleanField(default=False)
    moeda = models.CharField(max_length=3, default='BRL')
    msg_pdv = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Configuracao do Sistema'
        verbose_name_plural = 'Configuracoes do Sistema'

    def __str__(self):
        return f'Config {self.empresa}'


class ConfigFiscalSistema(BaseEmpresa):
    certificado_a1 = models.FileField(upload_to='certificados/', blank=True)
    certificado_senha = models.CharField(max_length=200, blank=True, default='')
    certificado_validade = models.DateField(null=True, blank=True)

    cnae = models.CharField(max_length=10, blank=True, default='')
    cnes = models.CharField(max_length=15, blank=True, default='')
    codigo_municipio = models.CharField(max_length=7, blank=True, default='')
    inscricao_municipal = models.CharField(max_length=20, blank=True, default='')
    perfil_ecf = models.CharField(max_length=1, default='A', choices=[
        ('A', 'A - ECF Sem Controle de Estoque'),
        ('B', 'B - ECF Sem Controle de Estoque com DAV'),
        ('C', 'C - ECF com Controle de Estoque'),
    ])

    nfe_ambiente = models.CharField(max_length=1, default='2', choices=[
        ('1', 'Producao'),
        ('2', 'Homologacao'),
    ])
    nfe_versao = models.CharField(max_length=4, default='4.00')
    nfe_serie = models.IntegerField(default=1)
    nfe_numero_atual = models.IntegerField(default=0)

    nfce_ambiente = models.CharField(max_length=1, default='2', choices=[
        ('1', 'Producao'),
        ('2', 'Homologacao'),
    ])
    nfce_versao = models.CharField(max_length=4, default='4.00')
    nfce_serie = models.IntegerField(default=1)
    nfce_numero_atual = models.IntegerField(default=0)
    nfce_csc_id = models.CharField(max_length=6, blank=True, default='')
    nfce_csc_token = models.CharField(max_length=36, blank=True, default='')

    sped_fiscal = models.BooleanField(default=False)
    sped_contabil = models.BooleanField(default=False)
    sped_contribuicoes = models.BooleanField(default=False)
    sintegra = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Configuracao Fiscal'
        verbose_name_plural = 'Configuracoes Fiscais'

    def __str__(self):
        return f'Fiscal {self.empresa}'


class ConfiguracaoMunicipal(BaseEmpresa):
    aliquota_issqn = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    aliquota_pis = models.DecimalField(max_digits=5, decimal_places=2, default=1.65)
    aliquota_cofins = models.DecimalField(max_digits=5, decimal_places=2, default=7.6)
    aliquota_icms_padrao = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    aliquota_fcp = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    cnae_principal = models.CharField(max_length=10, blank=True, default='')
    natureza_operacao = models.CharField(max_length=200, default='Venda de Mercadoria')
    regime_tributario = models.CharField(max_length=1, default='1', choices=[
        ('1', 'Simples Nacional'),
        ('2', 'Simples Nacional - Excesso de Sublimite'),
        ('3', 'Regime Normal'),
        ('4', 'Microempreendedor Individual (MEI)'),
    ])

    class Meta:
        verbose_name = 'Configuracao Municipal'
        verbose_name_plural = 'Configuracoes Municipais'

    def __str__(self):
        return f'Municipal {self.empresa}'


class ConfiguracaoEmail(BaseEmpresa):
    smtp_host = models.CharField(max_length=200, blank=True, default='')
    smtp_port = models.IntegerField(default=587)
    smtp_user = models.CharField(max_length=200, blank=True, default='')
    smtp_senha = models.CharField(max_length=200, blank=True, default='')
    smtp_usa_tls = models.BooleanField(default=True)
    email_remetente = models.CharField(max_length=200, blank=True, default='')
    nome_remetente = models.CharField(max_length=200, blank=True, default='pharmaMS')

    class Meta:
        verbose_name = 'Configuracao de Email'
        verbose_name_plural = 'Configuracoes de Email'

    def __str__(self):
        return f'Email {self.empresa}'


class ConfiguracaoBackup(BaseEmpresa):
    backup_automatico = models.BooleanField(default=False)
    backup_frequencia = models.CharField(max_length=10, default='diario', choices=[
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
    ])
    backup_hora = models.TimeField(default='02:00')
    backup_manter_dias = models.IntegerField(default=30)
    backup_local = models.CharField(max_length=200, default='/backups')
    ultimo_backup = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Configuracao de Backup'
        verbose_name_plural = 'Configuracoes de Backup'

    def __str__(self):
        return f'Backup {self.empresa}'
