from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseEmpresa


class Entrega(BaseEmpresa):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('atribuido', 'Atribuído'),
        ('em_rota', 'Em Rota'),
        ('entregue', 'Entregue'),
        ('cancelada', 'Cancelada'),
    ]
    venda = models.ForeignKey('vendas.Venda', on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey('cadastros.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    endereco_entrega = models.CharField(max_length=200)
    complemento = models.CharField(max_length=100, blank=True, default='')
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    contato_telefone = models.CharField('Telefone de Contato', max_length=20, blank=True, default='')
    observacoes = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    entregador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    taxa_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_entrega = models.DateField('Data da Entrega', null=True, blank=True)
    status_pendente_em = models.DateTimeField(null=True, blank=True)
    status_atribuido_em = models.DateTimeField(null=True, blank=True)
    status_em_rota_em = models.DateTimeField(null=True, blank=True)
    status_entregue_em = models.DateTimeField(null=True, blank=True)
    status_cancelada_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.cliente:
            return f'Entrega - {self.cliente.nome}'
        if self.venda:
            return f'Entrega Venda #{self.venda.numero_venda}'
        return f'Entrega #{self.pk}'

    def salvar_timestamp_status(self, status):
        ts = timezone.now()
        setattr(self, f'status_{status}_em', ts)
        self.status = status
        self.save(update_fields=[f'status_{status}_em', 'status'])

    class Meta:
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        ordering = ['-criado_em']
