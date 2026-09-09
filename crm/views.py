from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Campanha, ClienteCRM


@login_required
def index(request):
    campanhas = Campanha.objects.filter(empresa=request.empresa, ativo=True)
    clientes_crm = ClienteCRM.objects.filter(empresa=request.empresa).select_related('cliente')

    hoje = timezone.localdate()
    mes_inicio = hoje.replace(day=1)

    stats = {
        'total_clientes': clientes_crm.count(),
        'aniversariantes_mes': clientes_crm.filter(
            aniversario__month=hoje.month
        ).count(),
        'campanhas_ativas': campanhas.count(),
        'clientes_inativos_30d': clientes_crm.filter(
            ultima_compra__lt=hoje - timedelta(days=30)
        ).count() if clientes_crm.exists() else 0,
    }

    return render(request, 'crm/index.html', {
        'campanhas': campanhas,
        'clientes_crm': clientes_crm[:20],
        'stats': stats,
    })


@login_required
def campanha_nova(request):
    if request.method == 'POST':
        campanha = Campanha(
            empresa=request.empresa,
            nome=request.POST.get('nome', ''),
            descricao=request.POST.get('descricao', ''),
            data_inicio=request.POST.get('data_inicio'),
            data_fim=request.POST.get('data_fim'),
        )
        campanha.save()
        messages.success(request, 'Campanha criada com sucesso.')
        return redirect('crm:index')
    return render(request, 'crm/campanha_form.html')


@login_required
def campanha_editar(request, pk):
    campanha = get_object_or_404(Campanha, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        campanha.nome = request.POST.get('nome', campanha.nome)
        campanha.descricao = request.POST.get('descricao', campanha.descricao)
        campanha.data_inicio = request.POST.get('data_inicio', campanha.data_inicio)
        campanha.data_fim = request.POST.get('data_fim', campanha.data_fim)
        campanha.ativo = 'ativo' in request.POST
        campanha.save()
        messages.success(request, 'Campanha atualizada.')
        return redirect('crm:index')
    return render(request, 'crm/campanha_form.html', {'campanha': campanha})


@login_required
def campanha_excluir(request, pk):
    campanha = get_object_or_404(Campanha, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        campanha.delete()
        messages.success(request, 'Campanha excluida.')
    return redirect('crm:index')


@login_required
def cliente_crm(request, cliente_pk):
    cliente_crm, created = ClienteCRM.objects.get_or_create(
        empresa=request.empresa, cliente_id=cliente_pk
    )
    if request.method == 'POST':
        cliente_crm.aniversario = request.POST.get('aniversario') or None
        cliente_crm.observacoes = request.POST.get('observacoes', '')
        cliente_crm.save()
        messages.success(request, 'Perfil CRM atualizado.')
        return redirect('cadastros:clientes')

    from cadastros.models import Cliente
    cliente = get_object_or_404(Cliente, pk=cliente_pk, empresa=request.empresa)
    return render(request, 'crm/cliente_crm.html', {
        'perfil_crm': cliente_crm,
        'cliente': cliente,
    })


@login_required
def api_aniversariantes(request):
    hoje = timezone.localdate()
    clientes = ClienteCRM.objects.filter(
        empresa=request.empresa,
        aniversario__month=hoje.month
    ).select_related('cliente').values(
        'cliente__nome', 'aniversario'
    )[:10]
    return JsonResponse(list(clientes), safe=False)
