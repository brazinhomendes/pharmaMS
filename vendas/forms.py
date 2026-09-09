from django import forms
from .models import RegraComissao, Promocao


class RegraComissaoForm(forms.ModelForm):
    class Meta:
        model = RegraComissao
        fields = [
            'tipo', 'produto', 'classe_terapeutica', 'vendedor',
            'percentual', 'data_inicio', 'data_fim', 'ativo',
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }


class PromocaoForm(forms.ModelForm):
    class Meta:
        model = Promocao
        fields = [
            'nome', 'tipo', 'produto', 'classe_terapeutica',
            'percentual_desconto', 'quantidade_minima', 'quantidade_cobrar',
            'preco_promocional', 'data_inicio', 'data_fim',
            'dias_semana', 'ativo', 'limite_por_cliente',
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }
