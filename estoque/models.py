from django.db import models
from django.conf import settings
from datetime import date
from core.models import BaseEmpresa


class Lote(BaseEmpresa):
    produto = models.ForeignKey(
        'cadastros.Produto', on_delete=models.CASCADE, related_name='lotes'
    )
    codigo_lote = models.CharField(max_length=50)
    data_fabricacao = models.DateField(null=True, blank=True)
    data_validade = models.DateField()
    quantidade = models.IntegerField(default=0)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fornecedor = models.ForeignKey(
        'cadastros.Fornecedor', on_delete=models.SET_NULL, null=True, blank=True
    )
    nota_fiscal = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Lote'
        ordering = ['-data_validade']

    def __str__(self):
        return f'{self.produto.nome} - {self.codigo_lote}'

    @property
    def dias_para_vencer(self):
        if self.data_validade:
            delta = (self.data_validade - date.today()).days
            return delta
        return 0

    @property
    def esta_vencido(self):
        return self.data_validade < date.today() if self.data_validade else False

    @property
    def valor_total(self):
        return self.quantidade * self.preco_custo


class MovimentoEstoque(BaseEmpresa):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saida'),
        ('ajuste', 'Ajuste'),
        ('perda', 'Perda'),
        ('devolucao', 'Devolucao'),
        ('transferencia', 'Transferencia'),
    ]
    produto = models.ForeignKey(
        'cadastros.Produto', on_delete=models.CASCADE, related_name='movimentos'
    )
    lote = models.ForeignKey(
        Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimentos'
    )
    tipo = models.CharField(max_length=13, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    saldo_anterior = models.IntegerField(default=0)
    saldo_posterior = models.IntegerField(default=0)
    documento = models.CharField(max_length=50, blank=True, help_text='NF, receipt etc')
    observacao = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Movimento Estoque'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.tipo} - {self.produto.nome} x{self.quantidade}'
