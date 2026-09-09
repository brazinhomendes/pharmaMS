from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from core.models import BaseEmpresa


class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('O username é obrigatório')
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('perfil', 'admin_master')
        return self.create_user(username, email, password, **extra_fields)


PERFIL_APROVADOR_CHOICES = [
    ('gerente', 'Gerente'),
    ('supervisor', 'Supervisor'),
    ('admin', 'Administrador'),
]


def tem_perfil_aprovador(user):
    perfis_aprovadores = ['admin_master', 'admin_empresa', 'gerente', 'supervisor']
    return getattr(user, 'perfil', '') in perfis_aprovadores


class Usuario(AbstractBaseUser, PermissionsMixin):
    PERFIL_CHOICES = [
        ('admin_master', 'Admin Master'),
        ('admin_empresa', 'Admin Empresa'),
        ('gerente', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('farmaceutico', 'Farmaceutico'),
        ('atendente', 'Atendente'),
        ('entregador', 'Entregador'),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    nome_completo = models.CharField(max_length=200)
    empresa_ativa = models.ForeignKey(
        'empresas.Empresa', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='empresa_set'
    )
    telefone = models.CharField(max_length=20, blank=True, default='')
    perfil = models.CharField(max_length=30, choices=PERFIL_CHOICES, default='atendente')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nome_completo']

    def get_perfil_display(self):
        return dict(self.PERFIL_CHOICES).get(self.perfil, '')

    def __str__(self):
        return self.nome_completo or self.username

    class Meta:
        verbose_name = 'Usuario'


class SolicitacaoLiberacao(BaseEmpresa):
    TIPO_CHOICES = [
        ('cancelar_venda', 'Cancelar Venda'),
        ('cancelar_dav', 'Cancelar DAV'),
        ('cancelar_nfce', 'Cancelar NFC-e'),
        ('desconto_especial', 'Desconto Especial'),
        ('reabrir_caixa', 'Reabrir Caixa'),
        ('ajuste_estoque', 'Ajuste de Estoque'),
        ('outro', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='solicitacoes_feitas'
    )
    aprovador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='solicitacoes_aprovadas'
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pendente'
    )
    venda = models.ForeignKey(
        'vendas.Venda', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    dav = models.ForeignKey(
        'vendas.DAV', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    nfce = models.ForeignKey(
        'fiscal.NFe', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    motivo = models.TextField()
    observacao_aprovador = models.TextField(blank=True, default='')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.tipo} - {self.status}'

    class Meta:
        verbose_name = 'Solicitacao de Liberacao'
        verbose_name_plural = 'Solicitacoes de Liberacao'
        ordering = ['-data_solicitacao']


class RegraLiberacao(BaseEmpresa):
    TIPO_CHOICES = SolicitacaoLiberacao.TIPO_CHOICES
    PERFIL_APROVADOR_CHOICES = [
        ('gerente', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Administrador'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    perfil_aprovador = models.CharField(
        max_length=20, choices=PERFIL_APROVADOR_CHOICES
    )
    valor_minimo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.tipo} -> {self.perfil_aprovador}'

    class Meta:
        verbose_name = 'Regra de Liberacao'
        verbose_name_plural = 'Regras de Liberacao'


class HistoricoCancelamento(BaseEmpresa):
    TIPO_CHOICES = [
        ('venda', 'Venda'),
        ('dav', 'DAV'),
        ('nfce', 'NFC-e'),
        ('lancamento', 'Lancamento Financeiro'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    objeto_id = models.IntegerField()
    objeto_str = models.CharField(max_length=200)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    motivo = models.TextField()
    data_hora = models.DateTimeField(auto_now_add=True)
    liberacao = models.ForeignKey(
        SolicitacaoLiberacao, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f'{self.tipo} #{self.objeto_id}'

    class Meta:
        verbose_name = 'Historico de Cancelamento'
        verbose_name_plural = 'Historicos de Cancelamento'
        ordering = ['-data_hora']
