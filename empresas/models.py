from django.db import models
from core.models import BaseModel


class Empresa(BaseModel):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    ie = models.CharField(max_length=20, blank=True, default='')
    endereco = models.CharField(max_length=255, blank=True, default='')
    bairro = models.CharField(max_length=100, blank=True, default='')
    cidade = models.CharField(max_length=100, blank=True, default='')
    uf = models.CharField(max_length=2, blank=True, default='')
    cep = models.CharField(max_length=9, blank=True, default='')
    telefone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    logo = models.ImageField(upload_to='logos/', blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
