from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta


class LoteModelTest(TestCase):
    def setUp(self):
        from empresas.models import Empresa
        from cadastros.models import Produto
        self.empresa = Empresa.objects.create(
            nome='Farmacia Teste', cnpj='00.000.000/0001-00'
        )
        self.produto = Produto.objects.create(
            empresa=self.empresa, nome='Paracetamol 500mg',
            preco_venda=Decimal('8.99'), preco_custo=Decimal('3.50'),
            codigo_barras='7891234567891', estoque_minimo=10,
        )

    def test_lote_creation(self):
        from estoque.models import Lote
        lote = Lote.objects.create(
            empresa=self.empresa, produto=self.produto,
            codigo_lote='LOT001', quantidade=100,
            data_validade=date.today() + timedelta(days=365),
            preco_custo=Decimal('3.50'),
        )
        self.assertEqual(lote.quantidade, 100)
        self.assertTrue(lote.data_validade > date.today())

    def test_lote_vencido(self):
        from estoque.models import Lote
        lote = Lote.objects.create(
            empresa=self.empresa, produto=self.produto,
            codigo_lote='LOT002', quantidade=50,
            data_validade=date.today() - timedelta(days=10),
            preco_custo=Decimal('3.50'),
        )
        self.assertTrue(lote.data_validade < date.today())
