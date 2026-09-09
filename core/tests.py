from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class RateLimitTest(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_login_with_valid_credentials(self):
        User.objects.create_user(
            username='testuser', password='testpass123',
            empresa_ativa=None
        )
        response = self.client.post('/usuarios/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_rate_limit_locks_after_max_attempts(self):
        from django.core.cache import cache
        ip = '127.0.0.1'
        key = f'login_attempts:{ip}'
        for i in range(6):
            self.client.post('/usuarios/login/', {
                'username': 'nonexistent',
                'password': 'wrong',
            })
        attempts = cache.get(key, 0)
        self.assertGreaterEqual(attempts, 5)


class AuditLogTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='audituser', password='testpass123',
            empresa_ativa=None
        )

    def test_audit_log_creation(self):
        from core.audit_models import AuditLog
        log = AuditLog.objects.create(
            usuario=self.user,
            acao='login',
            descricao='POST /usuarios/login/',
            ip_address='127.0.0.1',
        )
        self.assertEqual(log.acao, 'login')
        self.assertEqual(log.usuario, self.user)
        self.assertIsNotNone(log.timestamp)


class LGPDModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='lgpduser', password='testpass123',
            empresa_ativa=None
        )

    def test_consentimento_creation(self):
        from core.audit_models import ConsentimentoLGPD
        c = ConsentimentoLGPD.objects.create(
            usuario=self.user,
            tipo='privacidade',
            aceito=True,
            ip_address='127.0.0.1',
        )
        self.assertTrue(c.aceito)
        self.assertEqual(str(c), f'{self.user} - Politica de Privacidade - Aceito')

    def test_politica_privacidade(self):
        from core.audit_models import PoliticaPrivacidade
        p = PoliticaPrivacidade.objects.create(
            titulo='Politica Teste',
            conteudo='Conteudo da politica',
            versao='1.0',
        )
        self.assertEqual(str(p), 'Politica Teste v1.0')


class DashboardAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashuser', password='testpass123',
            empresa_ativa=None
        )
        self.client.login(username='dashuser', password='testpass123')

    def test_api_dashboard_returns_json(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('vendas_hoje', data)
        self.assertIn('clientes_ativos', data)
        self.assertIn('produtos_em_estoque', data)
        self.assertIn('ticket_medio', data)
        self.assertIn('variacao_vendas', data)
