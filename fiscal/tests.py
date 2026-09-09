from django.test import TestCase


class NFeChoicesTest(TestCase):
    def test_nfce_status_choices(self):
        from fiscal.models import NFCe
        choices = dict(NFCe.STATUS_CHOICES)
        self.assertIn('pendente', choices)
        self.assertIn('autorizada', choices)
        self.assertIn('cancelada', choices)

    def test_nfe_model_fields(self):
        from fiscal.models import NFe
        fields = [f.name for f in NFe._meta.get_fields()]
        self.assertIn('chave_acesso', fields)
        self.assertIn('numero', fields)
        self.assertIn('serie', fields)
