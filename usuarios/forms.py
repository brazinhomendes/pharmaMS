from django import forms
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha', widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nome_completo', 'telefone', 'perfil', 'is_active']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
