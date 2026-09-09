from django import forms
from .models import Empresa


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Razao Social da empresa',
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00',
                'data-mask': 'cnpj',
            }),
            'ie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Inscricao Estadual (opcional)',
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, numero - complemento',
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
            }),
            'uf': forms.Select(attrs={
                'class': 'form-select',
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'data-mask': 'cep',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'data-mask': 'phone',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contato@empresa.com.br',
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
