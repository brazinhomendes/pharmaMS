import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Q
from django.conf import settings
from django.utils import timezone

from .models import Caixa, MovimentoCaixa
from vendas.models import Venda, ItemVenda, FaturaVenda
from vendas.services import calcular_comissao, aplicar_promocoes


@login_required
def index(request):
    caixa_atual = Caixa.objects.filter(
        empresa=request.empresa,
        status='aberto',
        usuario_abertura=request.user
    ).first()

    context = {'caixa_atual': caixa_atual}

    if caixa_atual:
        vendas = Venda.objects.filter(
            empresa=request.empresa,
            data_venda__date=timezone.localdate(),
            status='finalizada'
        )
        context['vendas_hoje'] = vendas

    return render(request, 'pdv/index.html', context)


@login_required
def abrir_caixa(request):
    if request.method != 'POST':
        return redirect('pdv:index')

    caixa_aberto = Caixa.objects.filter(
        empresa=request.empresa,
        status='aberto',
        usuario_abertura=request.user
    ).first()

    if caixa_aberto:
        messages.warning(request, 'Voce ja possui um caixa aberto.')
        return redirect('pdv:index')

    saldo_inicial = request.POST.get('saldo_inicial', 0)
    try:
        saldo_inicial = float(saldo_inicial)
    except (ValueError, TypeError):
        saldo_inicial = 0

    Caixa.objects.create(
        empresa=request.empresa,
        usuario_abertura=request.user,
        saldo_inicial=saldo_inicial,
    )

    messages.success(request, 'Caixa aberto com sucesso.')
    return redirect('pdv:index')


@login_required
def fechar_caixa(request):
    caixa = Caixa.objects.filter(
        empresa=request.empresa,
        status='aberto',
        usuario_abertura=request.user
    ).first()

    if not caixa:
        messages.error(request, 'Nenhum caixa aberto encontrado.')
        return redirect('pdv:index')

    vendas_caixa = Venda.objects.filter(
        empresa=request.empresa,
        movimentocaixa__caixa=caixa,
        movimentocaixa__tipo='entrada',
        status='finalizada'
    )

    pagamento_map = {
        'dinheiro': 'especie',
        'credito': 'cartao', 'debito': 'cartao',
        'credito_pbm': 'cartao', 'debito_pbm': 'cartao',
        'pix': 'pix',
    }

    expected = {'especie': 0, 'cartao': 0, 'pix': 0, 'convenio': 0}

    for venda in vendas_caixa:
        categoria = pagamento_map.get(venda.forma_pagamento, 'convenio')
        expected[categoria] += float(venda.total)

    outras_entradas = caixa.movimentos.filter(
        tipo='entrada', venda__isnull=True
    ).aggregate(total=Sum('valor'))['total'] or 0

    if request.method == 'GET':
        aggs = caixa.movimentos.aggregate(
            total_saidas=Sum('valor', filter=Q(tipo='saida')),
            total_sangrias=Sum('valor', filter=Q(tipo='sangria')),
            total_suprimentos=Sum('valor', filter=Q(tipo='suprimento')),
        )
        context = {
            'caixa': caixa,
            'expected_especie': expected['especie'],
            'expected_cartao': expected['cartao'],
            'expected_pix': expected['pix'],
            'expected_convenio': expected['convenio'],
            'outras_entradas': float(outras_entradas),
            'total_saidas': float(aggs['total_saidas'] or 0),
            'total_sangrias': float(aggs['total_sangrias'] or 0),
            'total_suprimentos': float(aggs['total_suprimentos'] or 0),
        }
        return render(request, 'pdv/fechar_caixa.html', context)

    saldo_em_especie = request.POST.get('saldo_em_especie', 0)
    saldo_em_cartao = request.POST.get('saldo_em_cartao', 0)
    saldo_em_pix = request.POST.get('saldo_em_pix', 0)
    saldo_em_convenio = request.POST.get('saldo_em_convenio', 0)
    observacoes = request.POST.get('observacoes_fechamento', '')

    try:
        saldo_em_especie = float(saldo_em_especie)
    except (ValueError, TypeError):
        saldo_em_especie = 0
    try:
        saldo_em_cartao = float(saldo_em_cartao)
    except (ValueError, TypeError):
        saldo_em_cartao = 0
    try:
        saldo_em_pix = float(saldo_em_pix)
    except (ValueError, TypeError):
        saldo_em_pix = 0
    try:
        saldo_em_convenio = float(saldo_em_convenio)
    except (ValueError, TypeError):
        saldo_em_convenio = 0

    total_contado = saldo_em_especie + saldo_em_cartao + saldo_em_pix + saldo_em_convenio

    aggs = caixa.movimentos.aggregate(
        total_entradas=Sum('valor', filter=Q(tipo='entrada')),
        total_saidas=Sum('valor', filter=Q(tipo='saida')),
        total_sangrias=Sum('valor', filter=Q(tipo='sangria')),
        total_suprimentos=Sum('valor', filter=Q(tipo='suprimento')),
    )
    total_entradas = float(aggs['total_entradas'] or 0)
    total_saidas = float(aggs['total_saidas'] or 0)
    total_sangrias = float(aggs['total_sangrias'] or 0)
    total_suprimentos = float(aggs['total_suprimentos'] or 0)

    saldo_esperado = (
        float(caixa.saldo_inicial)
        + total_entradas
        - total_saidas
        - total_sangrias
        + total_suprimentos
    )

    diferenca = total_contado - saldo_esperado

    caixa.saldo_em_especie = saldo_em_especie
    caixa.saldo_em_cartao = saldo_em_cartao
    caixa.saldo_em_pix = saldo_em_pix
    caixa.saldo_em_convenio = saldo_em_convenio
    caixa.saldo_final = total_contado
    caixa.saldo_esperado = saldo_esperado
    caixa.diferenca = diferenca
    caixa.observacoes_fechamento = observacoes
    caixa.data_fechamento = timezone.now()
    caixa.status = 'fechado'
    caixa.usuario_fechamento = request.user
    caixa.save()

    messages.success(request, 'Caixa fechado com sucesso.')
    return redirect('pdv:index')


@login_required
def api_finalizar_venda(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo nao permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalido'}, status=400)

    caixa = Caixa.objects.filter(
        empresa=request.empresa,
        status='aberto',
        usuario_abertura=request.user
    ).first()

    if not caixa:
        return JsonResponse({'error': 'Nenhum caixa aberto'}, status=400)

    items = data.get('items', [])
    if not items:
        return JsonResponse({'error': 'Nenhum item na venda'}, status=400)

    forma_pagamento = data.get('forma_pagamento', 'dinheiro')
    desconto = float(data.get('desconto', 0))
    observacoes = data.get('observacoes', '')
    cliente_id = data.get('cliente_id')

    subtotal = sum(
        float(item.get('preco_venda', 0)) * int(item.get('quantidade', 1))
        for item in items
    )
    total = subtotal - desconto

    ultimo_numero = Venda.objects.filter(empresa=request.empresa).aggregate(
        max_num=models.Max('numero_venda')
    )['max_num']
    novo_numero = str(int(ultimo_numero) + 1) if ultimo_numero else '1'

    cliente = None
    if cliente_id:
        from cadastros.models import Cliente
        cliente = get_object_or_404(Cliente, pk=cliente_id, empresa=request.empresa)

    valor_recebido = float(data.get('valor_recebido', 0))
    troco = max(0, valor_recebido - total)

    venda = Venda.objects.create(
        empresa=request.empresa,
        cliente=cliente,
        numero_venda=novo_numero,
        forma_pagamento=forma_pagamento,
        subtotal=subtotal,
        desconto=desconto,
        total=total,
        status='aberta',
        usuario=request.user,
        observacoes=observacoes,
        valor_recebido=valor_recebido,
        troco=troco,
    )

    for item in items:
        produto_id = item.get('produto_id') or item.get('id')
        quantidade = int(item.get('quantidade', 1))
        preco_unitario = float(item.get('preco_venda', 0))
        item_subtotal = preco_unitario * quantidade

        ItemVenda.objects.create(
            venda=venda,
            produto_id=produto_id,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            subtotal=item_subtotal,
        )

    desconto_promocional = aplicar_promocoes(venda)

    novo_subtotal = sum(
        float(item.subtotal) for item in venda.itens.all()
    )
    novo_total = novo_subtotal - desconto - desconto_promocional
    if novo_total < 0:
        novo_total = 0

    venda.subtotal = novo_subtotal
    venda.desconto = desconto + desconto_promocional
    venda.total = novo_total
    venda.status = 'finalizada'
    venda.save()

    FaturaVenda.objects.create(
        empresa=request.empresa,
        venda=venda,
        parcela=1,
        valor=novo_total,
        data_vencimento=date.today(),
        pago=(forma_pagamento != 'convenio'),
    )

    MovimentoCaixa.objects.create(
        empresa=request.empresa,
        caixa=caixa,
        tipo='entrada',
        valor=novo_total,
        descricao=f'Venda #{novo_numero}',
        venda=venda,
        usuario=request.user,
    )

    calcular_comissao(venda)

    if forma_pagamento != 'convenio':
        try:
            from fiscal.services import NFCeService
            emitente = request.empresa
            NFCeService.emitir_nfce(venda, emitente, tipo_emissao='2', justificativa='Venda offline - contingencia')
        except Exception:
            pass

    return JsonResponse({'success': True, 'venda_id': venda.pk, 'numero_venda': novo_numero})


@login_required
def api_buscar_produto_pdv(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)

    from django.apps import apps
    Produto = apps.get_model('cadastros', 'Produto')
    produtos = Produto.objects.filter(
        Q(empresa=request.empresa),
        Q(nome__icontains=q) | Q(codigo_barras__icontains=q),
        ativo=True
    )[:20]

    dados = [{
        'id': p.id,
        'nome': p.nome,
        'codigo_barras': p.codigo_barras,
        'preco_venda': str(p.preco_venda),
        'laboratorio': str(p.laboratorio) if p.laboratorio else '',
        'principio_ativo': p.principio_ativo or '',
        'controlado_anvisa': p.controlado_anvisa,
    } for p in produtos]

    return JsonResponse(dados, safe=False)


@login_required
def api_dados_caixa(request):
    caixa = Caixa.objects.filter(
        empresa=request.empresa,
        status='aberto',
        usuario_abertura=request.user
    ).first()

    if not caixa:
        return JsonResponse({'caixa_aberto': False})

    movimentos_count = caixa.movimentos.count()
    total_vendas = caixa.movimentos.filter(
        tipo='entrada', venda__isnull=False
    ).aggregate(total=Sum('valor'))['total'] or 0
    vendas_count = caixa.movimentos.filter(
        tipo='entrada', venda__isnull=False
    ).count()

    return JsonResponse({
        'caixa_aberto': True,
        'caixa_id': caixa.id,
        'saldo_inicial': str(caixa.saldo_inicial),
        'data_abertura': caixa.data_abertura.isoformat(),
        'movimentos_count': movimentos_count,
        'total_vendas': str(total_vendas),
        'vendas_count': vendas_count,
    })
