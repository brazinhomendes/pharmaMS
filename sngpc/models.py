from django.db import models
from core.models import BaseEmpresa, BaseModel


class ClasseTerapeuticaSNGPC(BaseModel):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=200)

    def __str__(self):
        return self.nome


class MedicamentoControlado(BaseEmpresa):
    produto = models.OneToOneField(
        'cadastros.Produto', on_delete=models.CASCADE
    )
    classe_terapeutica = models.ForeignKey(
        ClasseTerapeuticaSNGPC, on_delete=models.PROTECT
    )
    tipo_receita = models.CharField(
        max_length=20,
        choices=(
            ('amarela', 'Amarela (B1)'),
            ('azul', 'Azul (B2)'),
            ('branco_comum', 'Branco Comum'),
            ('branco_especial', 'Branco Especial'),
            ('antibiotico', 'Antibiotico'),
            ('retinoico', 'Retinoico'),
            ('anabolizante', 'Anabolizante'),
        ),
    )
    concentracao = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.produto.nome


class ProfissionalSaude(BaseModel):
    nome = models.CharField(max_length=200)
    conselho = models.CharField(
        max_length=10,
        choices=(
            ('CRM', 'CRM'),
            ('COREN', 'COREN'),
            ('CRO', 'CRO'),
            ('CRF', 'CRF'),
        ),
    )
    numero_conselho = models.CharField(max_length=30)
    uf_conselho = models.CharField(max_length=2)

    def __str__(self):
        return f'{self.nome} - {self.conselho} {self.numero_conselho} {self.uf_conselho}'


class Receituario(BaseEmpresa):
    numero_receita = models.CharField(max_length=30)
    paciente_nome = models.CharField(max_length=200)
    paciente_cpf = models.CharField(max_length=18, blank=True)
    profissional = models.ForeignKey(
        ProfissionalSaude, on_delete=models.PROTECT
    )
    data_emissao = models.DateField()
    data_validade = models.DateField()
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f'Receita #{self.numero_receita}'


class ItemReceituario(BaseModel):
    receituario = models.ForeignKey(
        Receituario, on_delete=models.CASCADE, related_name='itens'
    )
    medicamento = models.ForeignKey(
        MedicamentoControlado, on_delete=models.PROTECT
    )
    quantidade = models.IntegerField()
    posologia = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.medicamento.produto.nome


class MovimentacaoSNGPC(BaseEmpresa):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saida'),
        ('perda', 'Perda'),
        ('devolucao', 'Devolucao'),
        ('inventario', 'Inventario'),
    )
    medicamento = models.ForeignKey(
        MedicamentoControlado, on_delete=models.PROTECT
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    lote = models.CharField(max_length=50, blank=True)
    receituario = models.ForeignKey(
        Receituario, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    data_movimento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.medicamento} - {self.tipo} x{self.quantidade}'


class RelatorioSNGPC(BaseEmpresa):
    tipo = models.CharField(
        max_length=20,
        choices=(
            ('bspo', 'BSPO'),
            ('bmpo', 'BMPO'),
            ('rmnra', 'RMNRA'),
            ('rmnrb', 'RMNRB'),
            ('inventario', 'Inventario'),
        ),
    )
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    arquivo_xml = models.FileField(upload_to='sngpc/relatorios/', blank=True)
    processado = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.tipo} {self.periodo_inicio} a {self.periodo_fim}'
