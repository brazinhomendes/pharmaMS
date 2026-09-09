from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from .models import Usuario, SolicitacaoLiberacao, RegraLiberacao, HistoricoCancelamento

User = get_user_model()


class EmpresaFilter(admin.SimpleListFilter):
    title = 'Empresa'
    parameter_name = 'empresa_ativa'

    def lookups(self, request, model_admin):
        if request.user.perfil == 'admin_master':
            empresas = User.objects.filter(
                empresa_ativa__isnull=False
            ).values_list('empresa_ativa__id', 'empresa_ativa__nome').distinct()
        else:
            empresas = []
        return list(empresas)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(empresa_ativa_id=self.value())
        return queryset


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = [
        'username', 'nome_completo', 'email', 'empresa_display',
        'perfil_badge', 'is_active_badge', 'is_staff'
    ]
    list_filter = [EmpresaFilter, 'perfil', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'nome_completo', 'empresa_ativa__nome']
    ordering = ['username']
    list_per_page = 25

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informacoes Pessoais', {
            'fields': ('email', 'nome_completo', 'telefone')
        }),
        ('Empresa & Perfil', {
            'fields': ('empresa_ativa', 'perfil')
        }),
        ('Permissoes', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Datas Importantes', {
            'classes': ('collapse',),
            'fields': ('last_login',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'nome_completo', 'telefone',
                'password1', 'password2',
                'empresa_ativa', 'perfil',
                'is_active', 'is_staff', 'is_superuser',
            ),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('empresa_ativa')
        if request.user.perfil != 'admin_master':
            qs = qs.filter(empresa_ativa=request.user.empresa_ativa)
        return qs

    def empresa_display(self, obj):
        if obj.empresa_ativa:
            return obj.empresa_ativa.nome
        return '-'
    empresa_display.short_description = 'Empresa'
    empresa_display.admin_order_field = 'empresa_ativa__nome'

    def perfil_badge(self, obj):
        colors = {
            'admin_master': '#ef4444',
            'admin_empresa': '#f59e0b',
            'gerente': '#3b82f6',
            'supervisor': '#8b5cf6',
            'farmaceutico': '#10b981',
            'atendente': '#64748b',
            'entregador': '#0ea5e9',
        }
        color = colors.get(obj.perfil, '#64748b')
        label = obj.get_perfil_display()
        return mark_safe(f'<span style="color:{color};font-weight:600;">{label}</span>')
    perfil_badge.short_description = 'Perfil'

    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color:#10b981;">Ativo</span>')
        return mark_safe('<span style="color:#ef4444;">Inativo</span>')
    is_active_badge.short_description = 'Status'

    def has_view_permission(self, request, obj=None):
        if request.user.perfil == 'admin_master':
            return True
        if obj and obj.empresa_ativa_id == request.user.empresa_ativa_id:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.perfil == 'admin_master':
            return True
        if obj and obj.empresa_ativa_id == request.user.empresa_ativa_id:
            return request.user.perfil in ('admin_empresa', 'gerente')
        return False

    def has_add_permission(self, request):
        if request.user.perfil == 'admin_master':
            return True
        return request.user.perfil in ('admin_empresa', 'gerente')

    def has_delete_permission(self, request, obj=None):
        if request.user.perfil == 'admin_master':
            return True
        return False

    def save_model(self, request, obj, form, change):
        if not change and request.user.perfil != 'admin_master':
            obj.empresa_ativa = request.user.empresa_ativa
        super().save_model(request, obj, form, change)


@admin.register(SolicitacaoLiberacao)
class SolicitacaoLiberacaoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'usuario', 'status', 'empresa', 'data_solicitacao']
    list_filter = ['tipo', 'status', 'empresa']
    search_fields = ['usuario__nome_completo', 'motivo', 'empresa__nome']
    readonly_fields = ['data_solicitacao', 'data_aprovacao']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('usuario', 'empresa')
        if request.user.perfil != 'admin_master':
            qs = qs.filter(empresa=request.user.empresa_ativa)
        return qs


@admin.register(RegraLiberacao)
class RegraLiberacaoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'perfil_aprovador', 'valor_minimo', 'ativo', 'empresa']
    list_filter = ['tipo', 'perfil_aprovador', 'ativo', 'empresa']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.perfil != 'admin_master':
            qs = qs.filter(empresa=request.user.empresa_ativa)
        return qs


@admin.register(HistoricoCancelamento)
class HistoricoCancelamentoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'objeto_id', 'objeto_str', 'usuario', 'empresa', 'data_hora']
    list_filter = ['tipo', 'empresa']
    search_fields = ['objeto_str', 'motivo', 'usuario__username']
    readonly_fields = ['data_hora']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('usuario', 'empresa')
        if request.user.perfil != 'admin_master':
            qs = qs.filter(empresa=request.user.empresa_ativa)
        return qs
