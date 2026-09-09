import json
from datetime import timedelta, date

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import DecimalField
from django.utils import timezone

from vendas.models import Venda, ItemVenda, Promocao
from cadastros.models import Produto, Cliente
from usuarios.models import SolicitacaoLiberacao
from delivery.models import Entrega
from estoque.models import Lote


PAGAMENTO_CORES = {
    'dinheiro': '#10b981',
    'credito': '#3b82f6',
    'debito': '#8b5cf6',
    'pix': '#f59e0b',
    'convenio': '#ef4444',
    'credito_pbm': '#06b6d4',
    'debito_pbm': '#ec4899',
    'vale': '#84cc16',
    'multi': '#64748b',
}


@login_required
def dashboard(request):
    empresa = request.empresa
    hoje = timezone.localdate()
    mes_inicio = hoje.replace(day=1)

    vendas_hoje = Venda.objects.filter(
        empresa=empresa, status='finalizada', data_venda__date=hoje
    ).aggregate(total=Sum('total'))['total'] or 0

    produtos_em_estoque = Produto.objects.filter(
        empresa=empresa, lotes__quantidade__gt=0
    ).distinct().count()

    clientes_ativos = Cliente.objects.filter(empresa=empresa, ativo=True).count()

    pendentes = SolicitacaoLiberacao.objects.filter(
        empresa=empresa, status='pendente'
    ).count()

    # --- Estoque crítico ---
    estoque_sub = Lote.objects.filter(
        produto=OuterRef('pk'), empresa=empresa
    ).values('produto').annotate(total=Sum('quantidade')).values('total')

    produtos_estoque_baixo = Produto.objects.filter(
        empresa=empresa, ativo=True, estoque_minimo__gt=0
    ).annotate(
        estoque_atual=Coalesce(Subquery(estoque_sub), Value(0), output_field=DecimalField())
    ).filter(estoque_atual__lte=F('estoque_minimo')).order_by('estoque_atual')[:8]

    # --- Últimas entregas ---
    ultimas_entregas = Entrega.objects.filter(
        empresa=empresa
    ).select_related('cliente', 'entregador').order_by('-criado_em')[:5]

    # --- Produtos mais vendidos (mês) ---
    top_produtos = ItemVenda.objects.filter(
        venda__empresa=empresa, venda__status='finalizada',
        venda__data_venda__gte=mes_inicio
    ).values('produto__nome', 'produto_id').annotate(
        total_qtd=Sum('quantidade'),
        total_valor=Sum('subtotal')
    ).order_by('-total_qtd')[:5]

    # --- Ranking de vendedores (mês) ---
    ranking_vendedores = Venda.objects.filter(
        empresa=empresa, status='finalizada',
        data_venda__gte=mes_inicio, usuario__isnull=False
    ).values('usuario__nome_completo', 'usuario__username').annotate(
        total_vendas=Count('id'),
        total_valor=Sum('total')
    ).order_by('-total_valor')[:5]

    # --- Promoções ativas ---
    promocoes_ativas = Promocao.objects.filter(
        empresa=empresa, ativo=True,
        data_inicio__lte=hoje, data_fim__gte=hoje
    ).order_by('data_fim')[:5]

    # --- Gráfico 7 dias ---
    dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%d/%m') for d in dias]
    chart_data = []
    for d in dias:
        total = Venda.objects.filter(
            empresa=empresa, status='finalizada', data_venda__date=d
        ).aggregate(v=Sum('total'))['v'] or 0
        chart_data.append(float(total))

    # --- Gráfico pizza pagamentos ---
    vendas_por_pagamento = Venda.objects.filter(
        empresa=empresa, status='finalizada'
    ).values('forma_pagamento').annotate(
        total=Sum('total')
    ).order_by('-total')

    FORMA_PAGAMENTO_DICT = dict(Venda.FORMA_PAGAMENTO)
    pagamento_labels = []
    pagamento_data = []
    pagamento_colors = []
    for item in vendas_por_pagamento:
        pagamento_labels.append(
            FORMA_PAGAMENTO_DICT.get(item['forma_pagamento'], item['forma_pagamento'])
        )
        pagamento_data.append(float(item['total']))
        pagamento_colors.append(
            PAGAMENTO_CORES.get(item['forma_pagamento'], '#6366f1')
        )

    if not pagamento_labels:
        pagamento_labels = ['Sem dados']
        pagamento_data = [1]
        pagamento_colors = ['#e5e7eb']

    # --- Delivery KPIs ---
    entregas_hoje = Entrega.objects.filter(empresa=empresa, criado_em__date=hoje).count()
    entregas_pendentes = Entrega.objects.filter(empresa=empresa, status='pendente').count()
    entregas_em_rota = Entrega.objects.filter(empresa=empresa, status='em_rota').count()
    entregas_entregues_hoje = Entrega.objects.filter(empresa=empresa, status='entregue', criado_em__date=hoje).count()

    ultimas_vendas = Venda.objects.filter(
        empresa=empresa, status='finalizada'
    ).select_related('cliente').order_by('-data_venda')[:5]

    context = {
        'vendas_hoje': vendas_hoje,
        'produtos_em_estoque': produtos_em_estoque,
        'clientes_ativos': clientes_ativos,
        'pendentes': pendentes,
        'entregas_hoje': entregas_hoje,
        'entregas_pendentes': entregas_pendentes,
        'entregas_em_rota': entregas_em_rota,
        'entregas_entregues_hoje': entregas_entregues_hoje,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_data_json': json.dumps(chart_data),
        'pagamento_labels_json': json.dumps(pagamento_labels),
        'pagamento_data_json': json.dumps(pagamento_data),
        'pagamento_colors_json': json.dumps(pagamento_colors),
        'ultimas_vendas': ultimas_vendas,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'ultimas_entregas': ultimas_entregas,
        'top_produtos': top_produtos,
        'ranking_vendedores': ranking_vendedores,
        'promocoes_ativas': promocoes_ativas,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def api_dashboard(request):
    empresa = request.empresa
    hoje = timezone.localdate()
    mes_inicio = hoje.replace(day=1)
    ontem = hoje - timedelta(days=1)

    vendas_hoje = Venda.objects.filter(
        empresa=empresa, status='finalizada', data_venda__date=hoje
    ).aggregate(total=Sum('total'))['total'] or 0

    vendas_ontem = Venda.objects.filter(
        empresa=empresa, status='finalizada', data_venda__date=ontem
    ).aggregate(total=Sum('total'))['total'] or 0

    vendas_mes = Venda.objects.filter(
        empresa=empresa, status='finalizada', data_venda__gte=mes_inicio
    ).aggregate(total=Sum('total'))['total'] or 0

    clientes_ativos = Cliente.objects.filter(empresa=empresa, ativo=True).count()

    produtos_em_estoque = Produto.objects.filter(
        empresa=empresa, lotes__quantidade__gt=0
    ).distinct().count()

    total_clientes = Cliente.objects.filter(empresa=empresa).count()

    ticket_medio = 0
    vendas_count_hoje = Venda.objects.filter(
        empresa=empresa, status='finalizada', data_venda__date=hoje
    ).count()
    if vendas_count_hoje > 0:
        ticket_medio = float(vendas_hoje) / vendas_count_hoje

    estoque_sub = Lote.objects.filter(
        produto=OuterRef('pk'), empresa=empresa
    ).values('produto').annotate(total=Sum('quantidade')).values('total')

    produtos_estoque_baixo = Produto.objects.filter(
        empresa=empresa, ativo=True, estoque_minimo__gt=0
    ).annotate(
        estoque_atual=Coalesce(Subquery(estoque_sub), Value(0), output_field=DecimalField())
    ).filter(estoque_atual__lte=F('estoque_minimo')).count()

    entregas_hoje = Entrega.objects.filter(
        empresa=empresa, criado_em__date=hoje
    ).count()

    entregas_pendentes = Entrega.objects.filter(
        empresa=empresa, status='pendente'
    ).count()

    variacao = 0
    if vendas_ontem > 0:
        variacao = round(((float(vendas_hoje) - float(vendas_ontem)) / float(vendas_ontem)) * 100, 1)

    dados = {
        'vendas_hoje': float(vendas_hoje),
        'vendas_ontem': float(vendas_ontem),
        'vendas_mes': float(vendas_mes),
        'variacao_vendas': variacao,
        'clientes_ativos': clientes_ativos,
        'total_clientes': total_clientes,
        'produtos_em_estoque': produtos_em_estoque,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'ticket_medio': round(ticket_medio, 2),
        'vendas_count_hoje': vendas_count_hoje,
        'entregas_hoje': entregas_hoje,
        'entregas_pendentes': entregas_pendentes,
    }
    return JsonResponse(dados)
