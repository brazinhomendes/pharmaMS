from django.db import models
from django.conf import settings
from core.models import BaseEmpresa, BaseModel


class PedidoCompra(BaseEmpresa):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviado', 'Enviado'),
        ('recebido', 'Recebido'),
        ('parcial', 'Recebido Parcial'),
        ('cancelado', 'Cancelado'),
    ]
    numero_pedido = models.CharField(max_length=20, unique=True)
    fornecedor = models.ForeignKey(
        'cadastros.Fornecedor', on_delete=models.CASCADE, related_name='pedidos'
    )
    data_pedido = models.DateField(auto_now_add=True)
    data_previsao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='rascunho')
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = 'Pedido Compra'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Pedido #{self.numero_pedido} - {self.fornecedor.nome}'


class ItemPedidoCompra(BaseModel):
    pedido = models.ForeignKey(
        PedidoCompra, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey(
        'cadastros.Produto', on_delete=models.CASCADE, related_name='itens_compra'
    )
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_recebida = models.IntegerField(default=0)

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    @property
    def pendente(self):
        return self.quantidade - self.quantidade_recebida

    def __str__(self):
        return f'{self.produto.nome} x{self.quantidade}'


class SugestaoCompra(BaseEmpresa):
    data_geracao = models.DateField(auto_now_add=True)
    data_inicio_analise = models.DateField()
    data_fim_analise = models.DateField()
    processada = models.BooleanField(default=False)
    pedido = models.ForeignKey(
        'compras.PedidoCompra', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sugestoes'
    )

    class Meta:
        verbose_name = 'Sugestão de Compra'
        ordering = ['-data_geracao']

    def __str__(self):
        return f'Sugestão {self.data_geracao}'


class ItemSugestaoCompra(BaseModel):
    PRIORIDADE_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Média'),
        ('baixa', 'Baixa'),
    ]
    sugestao = models.ForeignKey(
        SugestaoCompra, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey('cadastros.Produto', on_delete=models.CASCADE)
    estoque_atual = models.IntegerField()
    estoque_minimo = models.IntegerField()
    vendas_periodo = models.IntegerField()
    dias_estoque = models.IntegerField()
    sugestao_compra = models.IntegerField()
    prioridade = models.CharField(max_length=5, choices=PRIORIDADE_CHOICES)
    aprovado = models.BooleanField(default=False)

    def __str__(self):
        return self.produto.nome


class NotaFiscalEntrada(BaseEmpresa):
    numero_nf = models.CharField(max_length=20)
    serie = models.CharField(max_length=5, blank=True)
    chave_acesso = models.CharField(max_length=50, blank=True)
    fornecedor = models.ForeignKey(
        'cadastros.Fornecedor', on_delete=models.CASCADE, related_name='nfs_entrada'
    )
    pedido = models.ForeignKey(
        PedidoCompra, on_delete=models.SET_NULL, null=True, blank=True, related_name='nfs'
    )
    data_emissao = models.DateField()
    data_recebimento = models.DateField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cfop = models.CharField(max_length=10, blank=True)
    arquivo_xml = models.FileField(upload_to='nfs/xml/', blank=True)
    processada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'NF Entrada'
        ordering = ['-criado_em']

    def __str__(self):
        return f'NF {self.numero_nf} - {self.fornecedor}'
