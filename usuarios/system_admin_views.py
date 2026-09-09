from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from .decorators import admin_master_required
from .forms import UsuarioForm
from empresas.models import Empresa
from vendas.models import Venda
from estoque.models import Lote
from cadastros.models import Produto, Cliente

User = get_user_model()


@admin_master_required
def dashboard(request):
    empresas_count = Empresa.objects.count()
    usuarios_count = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()

    empresas = Empresa.objects.annotate(
        usuarios_count=Count('empresa_set'),
        produtos_count=Count('empresa__produto', distinct=True),
    ).order_by('-criado_em')

    empresas_stats = []
    for emp in empresas:
        vendas_total = Venda.objects.filter(
            empresa=emp, status='finalizada'
        ).count()
        empresas_stats.append({
            'empresa': emp,
            'usuarios': emp.usuarios_count,
            'produtos': emp.produtos_count,
            'vendas': vendas_total,
        })

    return render(request, 'system_admin/dashboard.html', {
        'empresas_count': empresas_count,
        'usuarios_count': usuarios_count,
        'usuarios_ativos': usuarios_ativos,
        'empresas_stats': empresas_stats,
    })


@admin_master_required
def empresas_lista(request):
    busca = request.GET.get('q', '')
    empresas = Empresa.objects.annotate(
        usuarios_count=Count('empresa_set')
    )
    if busca:
        empresas = empresas.filter(
            Q(nome__icontains=busca) | Q(cnpj__icontains=busca)
        )
    empresas = empresas.order_by('-criado_em')
    return render(request, 'system_admin/empresas_lista.html', {
        'empresas': empresas,
        'busca': busca,
    })


@admin_master_required
def empresa_nova(request):
    if request.method == 'POST':
        empresa = Empresa(
            nome=request.POST.get('nome', ''),
            cnpj=request.POST.get('cnpj', ''),
            ie=request.POST.get('ie', ''),
            endereco=request.POST.get('endereco', ''),
            bairro=request.POST.get('bairro', ''),
            cidade=request.POST.get('cidade', ''),
            uf=request.POST.get('uf', ''),
            cep=request.POST.get('cep', ''),
            telefone=request.POST.get('telefone', ''),
            email=request.POST.get('email', ''),
        )
        empresa.save()
        messages.success(request, f'Empresa "{empresa.nome}" criada com sucesso.')
        return redirect('system_admin:empresas_lista')
    return render(request, 'system_admin/empresa_form.html', {'empresa': None})


@admin_master_required
def empresa_editar(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        empresa.nome = request.POST.get('nome', empresa.nome)
        empresa.cnpj = request.POST.get('cnpj', empresa.cnpj)
        empresa.ie = request.POST.get('ie', empresa.ie)
        empresa.endereco = request.POST.get('endereco', empresa.endereco)
        empresa.bairro = request.POST.get('bairro', empresa.bairro)
        empresa.cidade = request.POST.get('cidade', empresa.cidade)
        empresa.uf = request.POST.get('uf', empresa.uf)
        empresa.cep = request.POST.get('cep', empresa.cep)
        empresa.telefone = request.POST.get('telefone', empresa.telefone)
        empresa.email = request.POST.get('email', empresa.email)
        empresa.save()
        messages.success(request, f'Empresa "{empresa.nome}" atualizada.')
        return redirect('system_admin:empresas_lista')
    return render(request, 'system_admin/empresa_form.html', {'empresa': empresa})


@admin_master_required
def empresa_excluir(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        nome = empresa.nome
        empresa.delete()
        messages.success(request, f'Empresa "{nome}" excluida.')
    return redirect('system_admin:empresas_lista')


@admin_master_required
def usuarios_lista(request):
    empresa_id = request.GET.get('empresa')
    perfil = request.GET.get('perfil')
    busca = request.GET.get('q', '')

    usuarios = User.objects.select_related('empresa_ativa')

    if empresa_id:
        usuarios = usuarios.filter(empresa_ativa_id=empresa_id)
    if perfil:
        usuarios = usuarios.filter(perfil=perfil)
    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca) |
            Q(nome_completo__icontains=busca) |
            Q(email__icontains=busca)
        )

    usuarios = usuarios.order_by('-date_joined')

    empresas = Empresa.objects.order_by('nome')

    return render(request, 'system_admin/usuarios_lista.html', {
        'usuarios': usuarios,
        'empresas': empresas,
        'empresa_filtro': empresa_id,
        'perfil_filtro': perfil,
        'busca': busca,
        'PERFIL_CHOICES': User.PERFIL_CHOICES,
    })


@admin_master_required
def usuario_novo(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        nome_completo = request.POST.get('nome_completo', '')
        password = request.POST.get('password', '')
        empresa_id = request.POST.get('empresa_id')
        perfil = request.POST.get('perfil', 'atendente')
        telefone = request.POST.get('telefone', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username ja existe.')
            return redirect('system_admin:usuario_novo')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email ja cadastrado.')
            return redirect('system_admin:usuario_novo')

        empresa = None
        if empresa_id:
            empresa = get_object_or_404(Empresa, pk=empresa_id)

        user = User(
            username=username,
            email=email,
            nome_completo=nome_completo,
            empresa_ativa=empresa,
            perfil=perfil,
            telefone=telefone,
            is_staff=perfil in ('admin_master', 'admin_empresa'),
            is_active=True,
        )
        user.set_password(password)
        user.save()

        messages.success(request, f'Usuario "{user.username}" criado para {empresa.nome if empresa else "sistema"}.')
        return redirect('system_admin:usuarios_lista')

    empresas = Empresa.objects.order_by('nome')
    return render(request, 'system_admin/usuario_form.html', {
        'usuario': None,
        'empresas': empresas,
        'PERFIL_CHOICES': User.PERFIL_CHOICES,
    })


@admin_master_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        usuario.nome_completo = request.POST.get('nome_completo', usuario.nome_completo)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.telefone = request.POST.get('telefone', usuario.telefone)
        usuario.perfil = request.POST.get('perfil', usuario.perfil)
        usuario.is_active = 'is_active' in request.POST
        usuario.is_staff = usuario.perfil in ('admin_master', 'admin_empresa')

        empresa_id = request.POST.get('empresa_id')
        if empresa_id:
            usuario.empresa_ativa = get_object_or_404(Empresa, pk=empresa_id)
        else:
            usuario.empresa_ativa = None

        nova_senha = request.POST.get('password', '')
        if nova_senha:
            usuario.set_password(nova_senha)

        usuario.save()
        messages.success(request, f'Usuario "{usuario.username}" atualizado.')
        return redirect('system_admin:usuarios_lista')

    empresas = Empresa.objects.order_by('nome')
    return render(request, 'system_admin/usuario_form.html', {
        'usuario': usuario,
        'empresas': empresas,
        'PERFIL_CHOICES': User.PERFIL_CHOICES,
    })


@admin_master_required
def usuario_excluir(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if usuario.perfil == 'admin_master':
            messages.error(request, 'Nao e possivel excluir um admin master.')
            return redirect('system_admin:usuarios_lista')
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{username}" excluido.')
    return redirect('system_admin:usuarios_lista')


@admin_master_required
def api_empresa_usuarios(request, empresa_id):
    usuarios = User.objects.filter(
        empresa_ativa_id=empresa_id
    ).values('id', 'username', 'nome_completo', 'perfil', 'is_active')
    return JsonResponse(list(usuarios), safe=False)
