from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

User = get_user_model()


class VendaModelTest(TestCase):
    def setUp(self):
        from empresas.models import Empresa
        self.empresa = Empresa.objects.create(
            nome='Farmacia Teste', cnpj='00.000.000/0001-00'
        )
        self.user = User.objects.create_user(
            username='vendedor', password='test123',
            empresa_ativa=self.empresa
        )

    def test_promocao_calculo(self):
        from vendas.models import Promocao
        from cadastros.models import Produto
        produto = Produto.objects.create(
            empresa=self.empresa, nome='Dipirona',
            preco_venda=Decimal('10.00'), preco_custo=Decimal('5.00'),
            codigo_barras='7891234567890',
        )
        promo = Promocao.objects.create(
            empresa=self.empresa,
            nome='Promo Teste',
            tipo='percentual',
            valor=Decimal('10.00'),
            data_inicio=date.today(),
            data_fim=date.today(),
        )
        promo.produtos.add(produto)
        self.assertEqual(promo.valor, Decimal('10.00'))

    def test_forma_pagamento_choices(self):
        from vendas.models import Venda
        choices = dict(Venda.FORMA_PAGAMENTO)
        self.assertIn('dinheiro', choices)
        self.assertIn('pix', choices)
        self.assertIn('credito', choices)


class VendasViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        from empresas.models import Empresa
        self.empresa = Empresa.objects.create(
            nome='Farmacia Teste', cnpj='00.000.000/0001-00'
        )
        self.user = User.objects.create_user(
            username='vendedor', password='test123',
            empresa_ativa=self.empresa
        )
        self.client.login(username='vendedor', password='test123')

    def test_vendas_list_view(self):
        response = self.client.get('/vendas/')
        self.assertEqual(response.status_code, 200)
