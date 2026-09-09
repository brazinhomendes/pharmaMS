from django.db import models


class BaseModel(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        abstract = True


class EmpresaMixin(models.Model):
    empresa = models.ForeignKey(
        'empresas.Empresa', on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    class Meta:
        abstract = True


class BaseEmpresa(EmpresaMixin, BaseModel):
    class Meta:
        abstract = True
