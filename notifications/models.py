from django.db import models
from django.conf import settings
from core.models import BaseEmpresa


class Notificacao(BaseEmpresa):
    TIPO_CHOICES = [
        ('info', 'Info'),
        ('alerta', 'Alerta'),
        ('erro', 'Erro'),
        ('sucesso', 'Sucesso'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
