from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from .models import OperadoraPBM, TransacaoPBM, ItemTransacaoPBM


@login_required
def index(request):
    empresa = request.empresa
    operadoras = OperadoraPBM.objects.filter(ativo=True)
    transacoes_recentes = TransacaoPBM.objects.filter(
        empresa=empresa
    ).select_related('operadora', 'venda').order_by('-criado_em')[:10]

    stats = TransacaoPBM.objects.filter(empresa=empresa).aggregate(
        pendentes=Count('id', filter=models_filter(status='pendente')),
        autorizadas=Count('id', filter=models_filter(status='autorizada')),
        processadas=Count('id', filter=models_filter(status='processada')),
        total_valor=Sum('valor_total'),
    )

    return render(request, 'pbm/index.html', {
        'operadoras': operadoras,
        'transacoes_recentes': transacoes_recentes,
        'stats': stats,
    })


def models_filter(**kwargs):
    from django.db.models import Q
    return Q(**kwargs)


@login_required
def transacoes(request):
    empresa = request.empresa
    status = request.GET.get('status')
    operadora_id = request.GET.get('operadora')

    qs = TransacaoPBM.objects.filter(
        empresa=empresa
    ).select_related('operadora', 'venda').order_by('-criado_em')

    if status:
        qs = qs.filter(status=status)
    if operadora_id:
        qs = qs.filter(operadora_id=operadora_id)

    return render(request, 'pbm/transacoes.html', {
        'transacoes': qs,
        'status_filtro': status,
        'operadora_filtro': operadora_id,
        'STATUS_CHOICES': TransacaoPBM._meta.get_field('status').choices,
        'operadoras': OperadoraPBM.objects.filter(ativo=True),
    })


@login_required
def transacao_nova(request):
    if request.method == 'POST':
        from vendas.models import Venda
        venda_id = request.POST.get('venda_id')
        venda = get_object_or_404(Venda, pk=venda_id, empresa=request.empresa) if venda_id else None

        transacao = TransacaoPBM(
            empresa=request.empresa,
            operadora_id=request.POST.get('operadora_id'),
            venda=venda,
            valor_total=request.POST.get('valor_total', 0),
            valor_desconto=request.POST.get('valor_desconto', 0),
            valor_repassado=request.POST.get('valor_repassado', 0),
            numero_autorizacao=request.POST.get('numero_autorizacao', ''),
        )
        transacao.save()
        messages.success(request, 'Transacao PBM registrada.')
        return redirect('pbm:transacoes')

    operadoras = OperadoraPBM.objects.filter(ativo=True)
    return render(request, 'pbm/transacao_form.html', {'operadoras': operadoras})


@login_required
def transacao_detalhe(request, pk):
    transacao = get_object_or_404(
        TransacaoPBM, pk=pk, empresa=request.empresa
    )
    itens = ItemTransacaoPBM.objects.filter(transacao=transacao).select_related('produto')
    return render(request, 'pbm/transacao_detalhe.html', {
        'transacao': transacao,
        'itens': itens,
    })


@login_required
def transacao_atualizar_status(request, pk):
    if request.method == 'POST':
        transacao = get_object_or_404(TransacaoPBM, pk=pk, empresa=request.empresa)
        novo_status = request.POST.get('status')
        if novo_status in dict(TransacaoPBM._meta.get_field('status').choices):
            transacao.status = novo_status
            if novo_status == 'autorizada':
                transacao.numero_autorizacao = request.POST.get('numero_autorizacao', '')
                transacao.data_autorizacao = timezone.now()
            transacao.save()
            messages.success(request, f'Status atualizado para {transacao.get_status_display()}.')
    return redirect('pbm:transacao_detalhe', pk=pk)


@login_required
def operadora_nova(request):
    if request.method == 'POST':
        operadora = OperadoraPBM(
            nome=request.POST.get('nome', ''),
            tipo=request.POST.get('tipo', 'farmacia_popular'),
        )
        operadora.save()
        messages.success(request, 'Operadora criada.')
        return redirect('pbm:index')
    return render(request, 'pbm/operadora_form.html', {'OPERADORAS_TIPOS': OperadoraPBM._meta.get_field('tipo').choices})


@login_required
def api_transacoes_resumo(request):
    empresa = request.empresa
    resumo = TransacaoPBM.objects.filter(empresa=empresa).values('status').annotate(
        total=Count('id'),
        valor=Sum('valor_total')
    )
    return JsonResponse(list(resumo), safe=False)
