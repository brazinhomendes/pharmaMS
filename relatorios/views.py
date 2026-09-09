from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce, TruncDate
from django.db.models import DecimalField
from datetime import date, timedelta
from vendas.models import Venda, ItemVenda
from cadastros.models import Produto
from estoque.models import Lote
from financeiro.models import ContaPagar, ContaReceber


@login_required
def index(request):
    empresa = request.empresa
    hoje = date.today()

    vendas_hoje = Venda.objects.filter(
        empresa=empresa, data_venda__date=hoje, status='finalizada'
    ).aggregate(total=Coalesce(Sum('total'), Value(0), output_field=DecimalField()))['total']

    contas_pagar = ContaPagar.objects.filter(
        empresa=empresa, status='pendente'
    ).aggregate(total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField()))['total']

    contas_receber = ContaReceber.objects.filter(
        empresa=empresa, status='pendente'
    ).aggregate(total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField()))['total']

    estoque_sub = Lote.objects.filter(
        produto=OuterRef('pk'), empresa=empresa
    ).values('produto').annotate(total=Sum('quantidade')).values('total')

    produtos_estoque_baixo = Produto.objects.filter(
        empresa=empresa, ativo=True, estoque_minimo__gt=0
    ).annotate(
        estoque_atual=Coalesce(Subquery(estoque_sub), Value(0), output_field=DecimalField())
    ).filter(estoque_atual__lte=F('estoque_minimo'))

    return render(request, 'relatorios/index.html', {
        'vendas_hoje': vendas_hoje,
        'contas_pagar': contas_pagar,
        'contas_receber': contas_receber,
        'produtos_estoque_baixo': produtos_estoque_baixo.count(),
    })


@login_required
def rel_vendas(request):
    empresa = request.empresa
    hoje = date.today()
    data_inicio = request.GET.get('data_inicio', hoje.strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))
    forma_pagamento = request.GET.get('forma_pagamento', '')

    vendas = Venda.objects.filter(
        empresa=empresa, status='finalizada',
        data_venda__date__gte=data_inicio,
        data_venda__date__lte=data_fim,
    )
    if forma_pagamento:
        vendas = vendas.filter(forma_pagamento=forma_pagamento)

    total_geral = vendas.aggregate(total=Coalesce(Sum('total'), Value(0), output_field=DecimalField()))['total']
    total_desconto = vendas.aggregate(total=Coalesce(Sum('desconto'), Value(0), output_field=DecimalField()))['total']
    total_vendas = vendas.count()

    return render(request, 'relatorios/vendas.html', {
        'vendas': vendas.order_by('-data_venda'),
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'forma_pagamento': forma_pagamento,
        'total_geral': total_geral,
        'total_desconto': total_desconto,
        'total_vendas': total_vendas,
    })


@login_required
def rel_vendas_json(request):
    empresa = request.empresa
    days = int(request.GET.get('days', 7))
    hoje = date.today()
    inicio = hoje - timedelta(days=days - 1)

    vendas = Venda.objects.filter(
        empresa=empresa, status='finalizada',
        data_venda__date__gte=inicio,
        data_venda__date__lte=hoje,
    ).annotate(
        dia=TruncDate('data_venda')
    ).values('dia').annotate(
        total=Sum('total'),
        quantidade=Count('id')
    ).order_by('dia')

    data = [
        {
            'dia': v['dia'].strftime('%Y-%m-%d') if v['dia'] else '',
            'total': float(v['total']),
            'quantidade': v['quantidade'],
        }
        for v in vendas
    ]
    return JsonResponse(data, safe=False)


@login_required
def rel_produtos(request):
    empresa = request.empresa
    hoje = date.today()
    data_inicio = request.GET.get('data_inicio', (hoje - timedelta(days=30)).strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))

    produtos = ItemVenda.objects.filter(
        venda__empresa=empresa,
        venda__status='finalizada',
        venda__data_venda__date__gte=data_inicio,
        venda__data_venda__date__lte=data_fim,
    ).values(
        'produto__id', 'produto__nome'
    ).annotate(
        quantidade=Sum('quantidade'),
        total=Sum('subtotal'),
    ).order_by('-quantidade')[:50]

    return render(request, 'relatorios/produtos.html', {
        'produtos': produtos,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })


@login_required
def rel_produtos_json(request):
    empresa = request.empresa
    hoje = date.today()
    data_inicio = request.GET.get('data_inicio', (hoje - timedelta(days=30)).strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))

    produtos = ItemVenda.objects.filter(
        venda__empresa=empresa,
        venda__status='finalizada',
        venda__data_venda__date__gte=data_inicio,
        venda__data_venda__date__lte=data_fim,
    ).values(
        'produto__id', 'produto__nome'
    ).annotate(
        quantidade=Sum('quantidade'),
        total=Sum('subtotal'),
    ).order_by('-quantidade')[:20]

    data = [
        {
            'id': p['produto__id'],
            'nome': p['produto__nome'],
            'quantidade': int(p['quantidade']),
            'total': float(p['total']),
        }
        for p in produtos
    ]
    return JsonResponse(data, safe=False)


@login_required
def rel_clientes(request):
    empresa = request.empresa
    hoje = date.today()
    data_inicio = request.GET.get('data_inicio', (hoje - timedelta(days=365)).strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))
    clientes_qs = Venda.objects.filter(
        empresa=empresa, status='finalizada',
        cliente__isnull=False,
        data_venda__date__gte=data_inicio,
        data_venda__date__lte=data_fim,
    ).values(
        'cliente__id', 'cliente__nome'
    ).annotate(
        total_compras=Count('id'),
        valor_total=Sum('total'),
    ).order_by('-valor_total')[:50]

    clientes = []
    for c in clientes_qs:
        ticket_medio = float(c['valor_total']) / c['total_compras'] if c['total_compras'] else 0
        clientes.append({**c, 'ticket_medio': ticket_medio})

    return render(request, 'relatorios/clientes.html', {
        'clientes': clientes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })



@login_required
def rel_clientes_json(request):
    empresa = request.empresa
    hoje = date.today()
    data_inicio = request.GET.get('data_inicio', (hoje - timedelta(days=365)).strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))

    clientes_qs = Venda.objects.filter(
        empresa=empresa, status='finalizada',
        cliente__isnull=False,
        data_venda__date__gte=data_inicio,
        data_venda__date__lte=data_fim,
    ).values(
        'cliente__id', 'cliente__nome'
    ).annotate(
        total_compras=Count('id'),
        valor_total=Sum('total'),
    ).order_by('-valor_total')[:20]

    data = []
    for c in clientes_qs:
        ticket = float(c['valor_total']) / c['total_compras'] if c['total_compras'] else 0
        data.append({
            'id': c['cliente__id'],
            'nome': c['cliente__nome'],
            'compras': c['total_compras'],
            'total': float(c['valor_total']),
            'ticket_medio': round(ticket, 2),
        })
    return JsonResponse(data, safe=False)


@login_required
def rel_estoque(request):
    empresa = request.empresa
    hoje = date.today()
    dias = int(request.GET.get('dias', 60))

    estoque_sub = Lote.objects.filter(
        produto=OuterRef('pk'), empresa=empresa
    ).values('produto').annotate(total=Sum('quantidade')).values('total')

    produtos_estoque_baixo = Produto.objects.filter(
        empresa=empresa, ativo=True, estoque_minimo__gt=0
    ).annotate(
        estoque_atual=Coalesce(Subquery(estoque_sub), Value(0), output_field=DecimalField())
    ).filter(estoque_atual__lte=F('estoque_minimo'))

    produtos_sem_estoque = Produto.objects.filter(
        empresa=empresa, ativo=True
    ).annotate(
        estoque_atual=Coalesce(Subquery(estoque_sub), Value(0), output_field=DecimalField())
    ).filter(estoque_atual=0)

    lotes_proximos_validade = Lote.objects.filter(
        empresa=empresa, quantidade__gt=0,
        data_validade__gte=hoje,
        data_validade__lte=hoje + timedelta(days=dias),
    ).select_related('produto').order_by('data_validade')

    lotes_vencidos = Lote.objects.filter(
        empresa=empresa, quantidade__gt=0,
        data_validade__lt=hoje,
    ).select_related('produto').order_by('data_validade')

    return render(request, 'relatorios/estoque.html', {
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'produtos_sem_estoque': produtos_sem_estoque,
        'lotes_proximos_validade': lotes_proximos_validade,
        'lotes_vencidos': lotes_vencidos,
        'dias': dias,
    })


@login_required
def rel_financeiro(request):
    empresa = request.empresa
    hoje = date.today()

    contas_pagar = ContaPagar.objects.filter(empresa=empresa)
    contas_receber = ContaReceber.objects.filter(empresa=empresa)

    total_pagar_pendente = contas_pagar.filter(status='pendente').aggregate(
        total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField())
    )['total']
    total_pagar_vencido = contas_pagar.filter(
        status='pendente', data_vencimento__lt=hoje
    ).aggregate(total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField()))['total']
    total_pagar_pago = contas_pagar.filter(status='pago').aggregate(
        total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField())
    )['total']

    total_receber_pendente = contas_receber.filter(status='pendente').aggregate(
        total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField())
    )['total']
    total_receber_vencido = contas_receber.filter(
        status='pendente', data_vencimento__lt=hoje
    ).aggregate(total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField()))['total']
    total_receber_recebido = contas_receber.filter(status='pago').aggregate(
        total=Coalesce(Sum('valor'), Value(0), output_field=DecimalField())
    )['total']

    contas_pagar_list = contas_pagar.filter(
        status__in=['pendente', 'atrasada']
    ).order_by('data_vencimento')[:20]

    contas_receber_list = contas_receber.filter(
        status__in=['pendente', 'atrasada']
    ).order_by('data_vencimento')[:20]

    return render(request, 'relatorios/financeiro.html', {
        'total_pagar_pendente': total_pagar_pendente,
        'total_pagar_vencido': total_pagar_vencido,
        'total_pagar_pago': total_pagar_pago,
        'total_receber_pendente': total_receber_pendente,
        'total_receber_vencido': total_receber_vencido,
        'total_receber_recebido': total_receber_recebido,
        'contas_pagar_list': contas_pagar_list,
        'contas_receber_list': contas_receber_list,
        'today': hoje,
    })
