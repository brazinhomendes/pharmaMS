from django.contrib import admin
from .models import ContaPagar, ContaReceber, Lancamento

admin.site.register(ContaPagar)
admin.site.register(ContaReceber)
admin.site.register(Lancamento)
