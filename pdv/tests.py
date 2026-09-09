from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class CaixaModelTest(TestCase):
    def setUp(self):
        from empresas.models import Empresa
        self.empresa = Empresa.objects.create(
            nome='Farmacia Teste', cnpj='00.000.000/0001-00'
        )
        self.user = User.objects.create_user(
            username='operador', password='test123',
            empresa_ativa=self.empresa
        )

    def test_caixa_creation(self):
        from pdv.models import Caixa
        caixa = Caixa.objects.create(
            empresa=self.empresa, operador_abertura=self.user,
            status='aberto', saldo_inicial=200.00,
        )
        self.assertEqual(caixa.status, 'aberto')
        self.assertEqual(float(caixa.saldo_inicial), 200.00)


class PDVViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        from empresas.models import Empresa
        self.empresa = Empresa.objects.create(
            nome='Farmacia Teste', cnpj='00.000.000/0001-00'
        )
        self.user = User.objects.create_user(
            username='operador', password='test123',
            empresa_ativa=self.empresa
        )
        self.client.login(username='operador', password='test123')

    def test_pdv_index_view(self):
        response = self.client.get('/pdv/')
        self.assertEqual(response.status_code, 200)
