from django.db import models
from django.conf import settings
from core.models import BaseEmpresa


class Caixa(BaseEmpresa):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('fechado', 'Fechado'),
    ]
    usuario_abertura = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='caixas_abertos'
    )
    usuario_fechamento = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True, related_name='caixas_fechados'
    )
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_esperado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_em_especie = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Valor em dinheiro contado')
    saldo_em_cartao = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_em_pix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_em_convenio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    diferenca = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Diferenca entre esperado e contado')
    observacoes_fechamento = models.TextField(blank=True, default='')
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='aberto')

    def __str__(self):
        return f'Caixa #{self.id} - {self.usuario_abertura} - {self.data_abertura.date()}'


class MovimentoCaixa(BaseEmpresa):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saida'),
        ('sangria', 'Sangria'),
        ('suprimento', 'Suprimento'),
    ]
    caixa = models.ForeignKey(
        Caixa, on_delete=models.CASCADE, related_name='movimentos'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=200, blank=True, default='')
    venda = models.ForeignKey(
        'vendas.Venda', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.tipo} R$ {self.valor}'
