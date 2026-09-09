from django.db import models
from core.models import BaseEmpresa, BaseModel


class OperadoraPBM(BaseModel):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=20,
        choices=(
            ('farmacia_popular', 'Farmacia Popular'),
            ('vidalink', 'Vidalink'),
            ('orizon', 'Orizon'),
            ('trncentre', 'TRNCentre'),
            ('pharmalink', 'Pharmalink'),
            ('funcional_card', 'Funcional Card'),
            ('epharma', 'e-Pharma'),
        ),
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class TransacaoPBM(BaseEmpresa):
    operadora = models.ForeignKey(
        OperadoraPBM, on_delete=models.PROTECT
    )
    venda = models.ForeignKey(
        'vendas.Venda', on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('pendente', 'Pendente'),
            ('autorizada', 'Autorizada'),
            ('negada', 'Negada'),
            ('processada', 'Processada'),
            ('cancelada', 'Cancelada'),
        ),
        default='pendente',
    )
    numero_autorizacao = models.CharField(max_length=50, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_repassado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_autorizacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.operadora} - Venda #{self.venda.numero_venda}'


class ItemTransacaoPBM(BaseModel):
    transacao = models.ForeignKey(
        TransacaoPBM, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey(
        'cadastros.Produto', on_delete=models.PROTECT
    )
    quantidade = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_aprovado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.produto.nome
