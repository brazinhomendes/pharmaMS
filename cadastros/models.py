from django.db import models
from django.conf import settings
from core.models import BaseModel, BaseEmpresa


class ClasseTerapeutica(BaseModel):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Classe Terapêutica'
        verbose_name_plural = 'Classes Terapêuticas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Laboratorio(BaseModel):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)

    class Meta:
        verbose_name = 'Laboratório'
        verbose_name_plural = 'Laboratórios'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(BaseEmpresa):
    TIPO_MEDICAMENTO_CHOICES = [
        ('comum', 'Comum'),
        ('controlado', 'Controlado'),
        ('antibiotico', 'Antibiótico'),
        ('generico', 'Genérico'),
        ('similar', 'Similar'),
        ('manipulado', 'Manipulado'),
    ]

    codigo_barras = models.CharField('Código de Barras', max_length=20, blank=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    classe_terapeutica = models.ForeignKey(
        ClasseTerapeutica, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Classe Terapêutica'
    )
    laboratorio = models.ForeignKey(
        Laboratorio, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    principio_ativo = models.CharField('Princípio Ativo', max_length=200, blank=True)
    concentracao = models.CharField(max_length=100, blank=True, help_text='ex: 500mg')
    tipo_medicamento = models.CharField(
        'Tipo de Medicamento', max_length=20,
        choices=TIPO_MEDICAMENTO_CHOICES, default='comum'
    )
    precisa_receita = models.BooleanField('Precisa de Receita', default=False)
    unidade = models.CharField(max_length=10, blank=True, default='UN')
    preco_custo = models.DecimalField('Preço de Custo', max_digits=10, decimal_places=2, default=0)
    preco_venda = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2, default=0)
    margem_lucro = models.DecimalField('Margem de Lucro', max_digits=5, decimal_places=2, default=0)
    ncm = models.CharField('NCM', max_length=10, blank=True)
    cest = models.CharField('CEST', max_length=10, blank=True)
    codigo_anvisa = models.CharField('Código ANVISA', max_length=20, blank=True)
    estoque_minimo = models.IntegerField('Estoque Mínimo', default=0)
    estoque_maximo = models.IntegerField('Estoque Máximo', default=0)
    controlado_anvisa = models.BooleanField('Controlado ANVISA', default=False)
    curva_abc = models.CharField(
        'Curva ABC', max_length=1, choices=[('A','A'),('B','B'),('C','C')],
        default='C'
    )
    ultima_classificacao_abc = models.DateField('Última Classificação ABC', null=True, blank=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ClassificacaoABC(BaseEmpresa):
    data_calculo = models.DateField('Data do Cálculo', auto_now_add=True)
    total_produtos = models.IntegerField('Total de Produtos')
    total_vendas_periodo = models.DecimalField('Total de Vendas no Período', max_digits=15, decimal_places=2)
    concluida = models.BooleanField('Concluída', default=False)

    class Meta:
        verbose_name = 'Classificação ABC'
        verbose_name_plural = 'Classificações ABC'
        ordering = ['-data_calculo']

    def __str__(self):
        return f'ABC {self.data_calculo}'


class ModeloEtiqueta(BaseModel):
    nome = models.CharField(max_length=100)
    largura_mm = models.DecimalField('Largura (mm)', max_digits=5, decimal_places=1, default=40)
    altura_mm = models.DecimalField('Altura (mm)', max_digits=5, decimal_places=1, default=25)
    margem_superior = models.DecimalField('Margem Superior (mm)', max_digits=5, decimal_places=1, default=3)
    margem_inferior = models.DecimalField('Margem Inferior (mm)', max_digits=5, decimal_places=1, default=3)
    margem_esquerda = models.DecimalField('Margem Esquerda (mm)', max_digits=5, decimal_places=1, default=3)
    margem_direita = models.DecimalField('Margem Direita (mm)', max_digits=5, decimal_places=1, default=3)
    colunas = models.IntegerField('Colunas', default=3)
    linhas = models.IntegerField('Linhas', default=8)
    mostrar_nome = models.BooleanField('Mostrar Nome', default=True)
    mostrar_preco = models.BooleanField('Mostrar Preço', default=True)
    mostrar_codigo_barras = models.BooleanField('Mostrar Código de Barras', default=True)
    mostrar_preco_custo = models.BooleanField('Mostrar Preço de Custo', default=False)
    mostrar_laboratorio = models.BooleanField('Mostrar Laboratório', default=False)
    mostrar_validade = models.BooleanField('Mostrar Validade', default=False)
    fonte_tamanho = models.IntegerField('Tamanho da Fonte', default=10)
    cabecalho = models.CharField('Cabeçalho', max_length=200, blank=True)
    rodape = models.CharField('Rodapé', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Modelo de Etiqueta'
        verbose_name_plural = 'Modelos de Etiquetas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ImpressaoEtiqueta(BaseEmpresa):
    TIPO_ORIGEM_CHOICES = [
        ('produto', 'Produto'),
        ('lote', 'Lote'),
        ('classe', 'Classe Terapêutica'),
        ('todos', 'Todos Produtos'),
    ]
    modelo = models.ForeignKey(ModeloEtiqueta, on_delete=models.PROTECT, verbose_name='Modelo')
    tipo_origem = models.CharField('Tipo de Origem', max_length=10, choices=TIPO_ORIGEM_CHOICES)
    data_impressao = models.DateTimeField('Data de Impressão', auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Usuário')
    quantidade_copias = models.IntegerField('Quantidade de Cópias', default=1)

    class Meta:
        verbose_name = 'Impressão de Etiqueta'
        verbose_name_plural = 'Impressões de Etiquetas'
        ordering = ['-data_impressao']

    def __str__(self):
        return f'Etiquetas {self.data_impressao.date()}'


class ItemImpressaoEtiqueta(BaseModel):
    impressao = models.ForeignKey(ImpressaoEtiqueta, on_delete=models.CASCADE, related_name='itens', verbose_name='Impressão')
    produto = models.ForeignKey('cadastros.Produto', on_delete=models.CASCADE, verbose_name='Produto')
    lote = models.ForeignKey('estoque.Lote', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Lote')
    quantidade = models.IntegerField('Quantidade', default=1)

    class Meta:
        verbose_name = 'Item de Impressão'
        verbose_name_plural = 'Itens de Impressão'

    def __str__(self):
        return self.produto.nome


class Cliente(BaseEmpresa):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    nome = models.CharField(max_length=200)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=18, blank=True)
    rg = models.CharField('RG', max_length=20, blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    uf = models.CharField('UF', max_length=2, blank=True)
    cep = models.CharField('CEP', max_length=9, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Fornecedor(BaseEmpresa):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)
    ie = models.CharField('Inscrição Estadual', max_length=20, blank=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    uf = models.CharField('UF', max_length=2, blank=True)
    cep = models.CharField('CEP', max_length=9, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    contato_nome = models.CharField('Nome do Contato', max_length=100, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome
