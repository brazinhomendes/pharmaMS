from django.db import models
from django.conf import settings
from core.models import BaseEmpresa, BaseModel


class Venda(BaseEmpresa):
    FORMA_PAGAMENTO = [
        ('dinheiro', 'Dinheiro'), ('credito', 'Credito'),
        ('debito', 'Debito'), ('pix', 'Pix'),
        ('convenio', 'Convenio'), ('credito_pbm', 'Credito PBM'),
        ('debito_pbm', 'Debito PBM'), ('vale', 'Vale'),
        ('multi', 'Multiplas'),
    ]
    STATUS = [
        ('aberta', 'Aberta'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    cliente = models.ForeignKey(
        'cadastros.Cliente', on_delete=models.PROTECT,
        null=True, blank=True
    )
    numero_venda = models.CharField(max_length=20)
    data_venda = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(
        max_length=12, choices=FORMA_PAGAMENTO, default='dinheiro'
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default='aberta')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True, related_name='vendas_vendedor'
    )
    observacoes = models.TextField(blank=True, default='')
    nfce_emitida = models.BooleanField(default=False)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Valor pago pelo cliente')
    troco = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Troco a devolver')

    def __str__(self):
        return f'Venda #{self.numero_venda}'

    class Meta:
        ordering = ['-criado_em']


class ItemVenda(BaseModel):
    venda = models.ForeignKey(
        Venda, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey('cadastros.Produto', on_delete=models.PROTECT)
    lote = models.ForeignKey(
        'estoque.Lote', on_delete=models.PROTECT, null=True, blank=True
    )
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.produto.nome} x{self.quantidade}'


class FaturaVenda(BaseEmpresa):
    venda = models.ForeignKey(
        Venda, on_delete=models.CASCADE, related_name='faturas'
    )
    parcela = models.IntegerField(default=1)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f'Venda #{self.venda.numero_venda} - {self.parcela}o/{self.parcela}'


class RegraComissao(BaseEmpresa):
    TIPO_CHOICES = [
        ('produto', 'Por Produto'),
        ('classe', 'Por Classe'),
        ('geral', 'Geral'),
        ('vendedor', 'Por Vendedor'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    produto = models.ForeignKey(
        'cadastros.Produto', on_delete=models.CASCADE,
        null=True, blank=True
    )
    classe_terapeutica = models.ForeignKey(
        'cadastros.ClasseTerapeutica', on_delete=models.CASCADE,
        null=True, blank=True
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True
    )
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.tipo} - {self.percentual}%'

    class Meta:
        verbose_name = 'Regra Comissao'
        verbose_name_plural = 'Regras de Comissao'


class DAV(BaseEmpresa):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    numero = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(
        'cadastros.Cliente', on_delete=models.PROTECT,
        null=True, blank=True
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='aberto'
    )
    observacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    total_produtos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_descontos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_geral = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    venda = models.ForeignKey(
        'vendas.Venda', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dav_origem'
    )

    def __str__(self):
        return f'DAV {self.numero}'

    class Meta:
        verbose_name = 'DAV'
        verbose_name_plural = 'DAVs'
        ordering = ['-data_criacao']


class ItemDAV(BaseModel):
    dav = models.ForeignKey(
        DAV, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey('cadastros.Produto', on_delete=models.PROTECT)
    lote = models.ForeignKey(
        'estoque.Lote', on_delete=models.PROTECT, null=True, blank=True
    )
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.dav.numero} - {self.produto.nome}'


class Promocao(BaseEmpresa):
    TIPO_CHOICES = [
        ('produto', 'Por Produto'),
        ('classe', 'Por Classe'),
        ('geral', 'Geral'),
        ('quantidade', 'Leve X Pague Y'),
        ('combo', 'Combo'),
    ]
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    produto = models.ForeignKey(
        'cadastros.Produto', on_delete=models.CASCADE,
        null=True, blank=True
    )
    classe_terapeutica = models.ForeignKey(
        'cadastros.ClasseTerapeutica', on_delete=models.CASCADE,
        null=True, blank=True
    )
    percentual_desconto = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quantidade_minima = models.IntegerField(null=True, blank=True, help_text='Para leve X pague Y')
    quantidade_cobrar = models.IntegerField(null=True, blank=True, help_text='Pague Y itens')
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    dias_semana = models.CharField(max_length=50, blank=True, help_text='1,2,3,4,5,6,7 - dias da semana')
    ativo = models.BooleanField(default=True)
    limite_por_cliente = models.IntegerField(default=0, help_text='0 = ilimitado')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Promocao'
        verbose_name_plural = 'Promocoes'


class ComissaoVenda(BaseEmpresa):
    venda = models.ForeignKey(
        Venda, on_delete=models.CASCADE, related_name='comissoes'
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    item_venda = models.ForeignKey(
        ItemVenda, on_delete=models.SET_NULL, null=True, blank=True
    )
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2)
    valor_comissao = models.DecimalField(max_digits=10, decimal_places=2)
    paga = models.BooleanField(default=False)
    data_pagamento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.vendedor} - R$ {self.valor_comissao}'
