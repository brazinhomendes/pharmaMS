from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe
from .models import Empresa


class EmpresaUsuariosInline(admin.TabularInline):
    from django.contrib.auth import get_user_model
    model = get_user_model()
    fk_name = 'empresa_ativa'
    extra = 0
    fields = ['username', 'nome_completo', 'perfil', 'is_active']
    readonly_fields = ['username', 'nome_completo', 'perfil', 'is_active']
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'cidade', 'uf', 'usuarios_count', 'ativo_badge', 'criado_em']
    list_filter = ['uf', 'ativo']
    search_fields = ['nome', 'cnpj', 'ie', 'cidade']
    ordering = ['-criado_em']
    readonly_fields = ['criado_em', 'atualizado_em']

    fieldsets = (
        ('Dados Gerais', {
            'fields': ('nome', 'cnpj', 'ie', 'ativo')
        }),
        ('Endereco', {
            'fields': ('endereco', 'bairro', 'cidade', 'uf', 'cep')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Logotipo', {
            'fields': ('logo',)
        }),
        ('Metadados', {
            'classes': ('collapse',),
            'fields': ('criado_em', 'atualizado_em')
        }),
    )

    inlines = [EmpresaUsuariosInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.perfil == 'admin_master':
            return qs.annotate(
                _usuarios_count=Count('empresa_set')
            )
        return qs.filter(pk=request.user.empresa_ativa_id)

    def usuarios_count(self, obj):
        return getattr(obj, '_usuarios_count', obj.empresa_set.count())
    usuarios_count.short_description = 'Usuarios'
    usuarios_count.admin_order_field = '_usuarios_count'

    def ativo_badge(self, obj):
        if obj.ativo:
            return mark_safe('<span style="color:#10b981;font-weight:600;">Ativo</span>')
        return mark_safe('<span style="color:#ef4444;font-weight:600;">Inativo</span>')
    ativo_badge.short_description = 'Status'

    def has_view_permission(self, request, obj=None):
        if request.user.perfil == 'admin_master':
            return True
        if obj and obj.pk == request.user.empresa_ativa_id:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.perfil == 'admin_master':
            return True
        if obj and obj.pk == request.user.empresa_ativa_id:
            return request.user.perfil in ('admin_empresa', 'gerente')
        return False

    def has_add_permission(self, request):
        return request.user.perfil == 'admin_master'

    def has_delete_permission(self, request, obj=None):
        return request.user.perfil == 'admin_master'
