from django.db import models
from core.models import BaseEmpresa


class ContaPagar(BaseEmpresa):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelada', 'Cancelada'),
        ('atrasada', 'Atrasada'),
    ]
    fornecedor = models.ForeignKey('cadastros.Fornecedor', on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    documento = models.CharField(max_length=50, blank=True, default='')
    observacoes = models.TextField(blank=True, default='')

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'

    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'


class ContaReceber(BaseEmpresa):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelada', 'Cancelada'),
        ('atrasada', 'Atrasada'),
    ]
    cliente = models.ForeignKey('cadastros.Cliente', on_delete=models.CASCADE, null=True, blank=True)
    venda = models.ForeignKey('vendas.Venda', on_delete=models.CASCADE, null=True, blank=True)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_recebimento = models.DateField(null=True, blank=True)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'

    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'


class Lancamento(BaseEmpresa):
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
        ('transferencia', 'Transferencia'),
    ]
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_lancamento = models.DateField(auto_now_add=True)
    categoria = models.CharField(max_length=100, blank=True, default='')
    forma_pagamento = models.CharField(max_length=20, blank=True, default='')
    observacao = models.TextField(blank=True, default='')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return f'{self.tipo} - {self.descricao} R$ {self.valor}'

    class Meta:
        verbose_name = 'Lançamento'
        verbose_name_plural = 'Lançamentos'
