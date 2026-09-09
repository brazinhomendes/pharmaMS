from django.db import models
from core.models import BaseEmpresa


class Campanha(BaseEmpresa):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, default='')
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Campanha'
        verbose_name_plural = 'Campanhas'


class ClienteCRM(BaseEmpresa):
    cliente = models.OneToOneField('cadastros.Cliente', on_delete=models.CASCADE)
    aniversario = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True, default='')
    ultima_compra = models.DateField(null=True, blank=True)
    total_gasto = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.cliente.nome

    class Meta:
        verbose_name = 'Cliente CRM'
        verbose_name_plural = 'Clientes CRM'
