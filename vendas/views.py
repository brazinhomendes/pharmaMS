from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Venda, ItemVenda, RegraComissao, ComissaoVenda, Promocao, DAV, ItemDAV
from cadastros.models import Produto
from .forms import RegraComissaoForm, PromocaoForm


@login_required
def lista(request):
    from datetime import date
    hoje = date.today()

    vendas = Venda.objects.filter(empresa=request.empresa)
    status = request.GET.get('status')
    periodo = request.GET.get('periodo', 'todas')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if status and status != 'None':
        vendas = vendas.filter(status=status)

    if data_inicio and data_fim:
        vendas = vendas.filter(data_venda__date__gte=data_inicio, data_venda__date__lte=data_fim)
    elif periodo == 'hoje':
        vendas = vendas.filter(data_venda__date=hoje)
    elif periodo == 'mes':
        vendas = vendas.filter(data_venda__month=hoje.month, data_venda__year=hoje.year)
    elif periodo == '30d':
        from datetime import timedelta
        vendas = vendas.filter(data_venda__date__gte=hoje - timedelta(days=30))

    filtro_ativo = bool(data_inicio and data_fim) or periodo != 'todas' or (status and status != 'None')
    base = Venda.objects.filter(empresa=request.empresa)
    if filtro_ativo:
        total_periodo = vendas.aggregate(v=Sum('total'))['v'] or 0
        qtd_periodo = vendas.count()
        ticket_medio = float(total_periodo) / qtd_periodo if qtd_periodo else 0
        if data_inicio and data_fim:
            periodo_label = f'{data_inicio} a {data_fim}'
        elif periodo == 'hoje':
            periodo_label = 'Hoje'
        elif periodo == 'mes':
            periodo_label = 'Este Mês'
        elif periodo == '30d':
            periodo_label = 'Últimos 30 dias'
        elif status and status != 'None':
            periodo_label = status.title()
        else:
            periodo_label = 'Filtrado'
        total_hoje = total_mes = total_periodo
        qtd_hoje = qtd_mes = qtd_periodo
    else:
        total_hoje = base.filter(data_venda__date=hoje).aggregate(v=Sum('total'))['v'] or 0
        total_mes = base.filter(data_venda__month=hoje.month, data_venda__year=hoje.year).aggregate(v=Sum('total'))['v'] or 0
        qtd_hoje = base.filter(data_venda__date=hoje).count()
        qtd_mes = base.filter(data_venda__month=hoje.month, data_venda__year=hoje.year).count()
        ticket_medio = float(total_mes) / qtd_mes if qtd_mes else 0
        periodo_label = ''

    context = {
        'vendas': vendas.order_by('-data_venda'),
        'status_atual': status,
        'periodo_atual': periodo,
        'data_inicio': data_inicio or '',
        'data_fim': data_fim or '',
        'total_hoje': total_hoje,
        'total_mes': total_mes,
        'qtd_hoje': qtd_hoje,
        'qtd_mes': qtd_mes,
        'ticket_medio': ticket_medio,
        'periodo_label': periodo_label,
    }
    return render(request, 'vendas/lista.html', context)


@login_required
def detalhe(request, pk):
    venda = get_object_or_404(Venda, pk=pk, empresa=request.empresa)
    context = {'venda': venda}
    return render(request, 'vendas/detalhe.html', context)


@login_required
def cancelar(request, pk):
    venda = get_object_or_404(Venda, pk=pk, empresa=request.empresa)
    if venda.status != 'aberta':
        messages.error(request, 'Apenas vendas abertas podem ser canceladas.')
        return redirect('vendas:lista')

    from usuarios.services import LiberacaoService
    auto_aprovado, solicitacao = LiberacaoService.solicitar(
        tipo='cancelar_venda', usuario=request.user,
        empresa=request.empresa, objeto=venda,
        motivo='Cancelamento manual pelo usuario',
    )

    if auto_aprovado:
        venda.status = 'cancelada'
        venda.save()
        from usuarios.models import HistoricoCancelamento
        HistoricoCancelamento.objects.create(
            empresa=request.empresa,
            tipo='venda',
            objeto_id=venda.id,
            objeto_str=str(venda),
            usuario=request.user,
            motivo='Cancelamento manual',
        )
        messages.success(request, f'Venda #{venda.numero_venda} cancelada.')
    else:
        messages.success(request, f'Solicitacao de cancelamento da venda #{venda.numero_venda} enviada para aprovacao.')

    return redirect('vendas:lista')


@login_required
def api_ultimas_vendas(request):
    vendas = Venda.objects.filter(empresa=request.empresa).order_by('-data_venda')[:10]
    dados = [{
        'id': v.id,
        'numero': v.numero_venda,
        'total': str(v.total),
        'data': v.data_venda.isoformat(),
        'status': v.status,
    } for v in vendas]
    return JsonResponse(dados, safe=False)


@login_required
def comissoes(request):
    comissoes = ComissaoVenda.objects.filter(empresa=request.empresa)
    vendedores = comissoes.values(
        'vendedor', 'vendedor__nome_completo', 'vendedor__username'
    ).annotate(
        total=Sum('valor_comissao'),
        pendentes=Sum('valor_comissao', filter=Q(paga=False)),
    )
    context = {
        'comissoes': comissoes,
        'vendedores': vendedores,
    }
    return render(request, 'vendas/comissoes.html', context)


@login_required
def regras_comissao(request):
    regras = RegraComissao.objects.filter(empresa=request.empresa)
    return render(request, 'vendas/comissoes_regras.html', {'regras': regras})


@login_required
def regra_comissao_nova(request):
    if request.method == 'POST':
        form = RegraComissaoForm(request.POST)
        if form.is_valid():
            regra = form.save(commit=False)
            regra.empresa = request.empresa
            regra.save()
            messages.success(request, 'Regra de comissao criada.')
            return redirect('vendas:regras_comissao')
    else:
        form = RegraComissaoForm()
    return render(request, 'vendas/regra_comissao_form.html', {'form': form})


@login_required
def regra_comissao_editar(request, pk):
    regra = get_object_or_404(RegraComissao, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        form = RegraComissaoForm(request.POST, instance=regra)
        if form.is_valid():
            form.save()
            messages.success(request, 'Regra de comissao atualizada.')
            return redirect('vendas:regras_comissao')
    else:
        form = RegraComissaoForm(instance=regra)
    return render(request, 'vendas/regra_comissao_form.html', {'form': form})


@login_required
def comissoes_pagar(request):
    if request.method != 'POST':
        return redirect('vendas:comissoes')
    ids = request.POST.getlist('comissoes')
    if ids:
        ComissaoVenda.objects.filter(
            id__in=ids, empresa=request.empresa, paga=False
        ).update(paga=True)
        messages.success(request, f'{len(ids)} comissao(oes) marcada(s) como paga.')
    else:
        messages.warning(request, 'Nenhuma comissao selecionada.')
    return redirect('vendas:comissoes')


@login_required
def promocoes(request):
    promos = Promocao.objects.filter(empresa=request.empresa)
    return render(request, 'vendas/promocoes.html', {'promocoes': promos})


@login_required
def promocao_nova(request):
    if request.method == 'POST':
        form = PromocaoForm(request.POST)
        if form.is_valid():
            promo = form.save(commit=False)
            promo.empresa = request.empresa
            promo.save()
            messages.success(request, 'Promocao criada com sucesso.')
            return redirect('vendas:promocoes')
    else:
        form = PromocaoForm()
    return render(request, 'vendas/promocao_form.html', {'form': form})


@login_required
def promocao_editar(request, pk):
    promo = get_object_or_404(Promocao, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        form = PromocaoForm(request.POST, instance=promo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Promocao atualizada com sucesso.')
            return redirect('vendas:promocoes')
    else:
        form = PromocaoForm(instance=promo)
    return render(request, 'vendas/promocao_form.html', {'form': form})


@login_required
def promocao_ativar(request, pk):
    promo = get_object_or_404(Promocao, pk=pk, empresa=request.empresa)
    promo.ativo = not promo.ativo
    promo.save()
    status = 'ativada' if promo.ativo else 'desativada'
    messages.success(request, f'Promocao {status} com sucesso.')
    return redirect('vendas:promocoes')


@login_required
def davs(request):
    dav_list = DAV.objects.filter(empresa=request.empresa)
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    busca = request.GET.get('busca')

    if status and status != 'None':
        dav_list = dav_list.filter(status=status)
    if data_inicio:
        dav_list = dav_list.filter(data_criacao__date__gte=data_inicio)
    if data_fim:
        dav_list = dav_list.filter(data_criacao__date__lte=data_fim)
    if busca:
        dav_list = dav_list.filter(
            Q(numero__icontains=busca) | Q(cliente__nome__icontains=busca)
        )

    context = {
        'davs': dav_list,
        'status_atual': status,
    }
    return render(request, 'vendas/davs.html', context)


@login_required
def dav_novo(request):
    from django.utils import timezone
    today = timezone.localdate()
    prefix = f'DAV-{today.strftime("%Y%m%d")}-'
    last_today = DAV.objects.filter(
        empresa=request.empresa,
        numero__startswith=prefix
    ).count()
    novo_numero = f'{prefix}{last_today + 1:04d}'

    from django.contrib.auth import get_user_model
    User = get_user_model()
    from cadastros.models import Cliente
    clientes = Cliente.objects.filter(empresa=request.empresa)
    produtos_qs = Produto.objects.filter(empresa=request.empresa, ativo=True).annotate(
        estoque_atual=Sum('lotes__quantidade')
    )
    vendedores = User.objects.filter(empresa=request.empresa)

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        vendedor_id = request.POST.get('vendedor')
        observacoes = request.POST.get('observacoes', '')
        produtos_data = request.POST.getlist('produto_id')
        quantidades = request.POST.getlist('quantidade')
        precos = request.POST.getlist('preco_unitario')
        descontos = request.POST.getlist('desconto')
        subtotais = request.POST.getlist('subtotal')

        if not produtos_data:
            messages.error(request, 'Adicione pelo menos um produto.')
            return render(request, 'vendas/dav_form.html', {
                'produtos': produtos_qs,
                'clientes': clientes,
                'vendedores': vendedores,
                'novo_numero': novo_numero,
            })

        dav = DAV(
            empresa=request.empresa,
            numero=novo_numero,
            cliente_id=cliente_id or None,
            vendedor_id=vendedor_id or None,
            observacoes=observacoes,
        )

        total_produtos = 0
        total_descontos = 0
        total_geral = 0

        dav.save()

        for i in range(len(produtos_data)):
            if not produtos_data[i] or not quantidades[i]:
                continue
            qtd = Decimal(quantidades[i].replace(',', '.'))
            preco = Decimal(precos[i].replace(',', '.'))
            desc = Decimal(descontos[i].replace(',', '.')) if descontos[i] else Decimal('0')
            sub = Decimal(subtotais[i].replace(',', '.')) if subtotais[i] else (qtd * preco - desc)

            ItemDAV.objects.create(
                dav=dav,
                produto_id=produtos_data[i],
                quantidade=qtd,
                preco_unitario=preco,
                desconto=desc,
                subtotal=sub,
            )
            total_produtos += qtd * preco
            total_descontos += desc
            total_geral += sub

        dav.total_produtos = total_produtos
        dav.total_descontos = total_descontos
        dav.total_geral = total_geral
        dav.save()

        messages.success(request, f'DAV {dav.numero} criado com sucesso.')
        return redirect('vendas:dav_detalhe', pk=dav.pk)

    context = {
        'produtos': produtos_qs,
        'clientes': clientes,
        'vendedores': vendedores,
        'novo_numero': novo_numero,
    }
    return render(request, 'vendas/dav_form.html', context)


@login_required
def dav_detalhe(request, pk):
    dav = get_object_or_404(DAV, pk=pk, empresa=request.empresa)
    context = {'dav': dav}
    return render(request, 'vendas/dav_detalhe.html', context)


@login_required
def dav_editar(request, pk):
    dav = get_object_or_404(DAV, pk=pk, empresa=request.empresa)
    if dav.status != 'aberto':
        messages.error(request, 'Apenas DAVs abertos podem ser editados.')
        return redirect('vendas:dav_detalhe', pk=dav.pk)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    from cadastros.models import Cliente
    clientes = Cliente.objects.filter(empresa=request.empresa)
    produtos_qs = Produto.objects.filter(empresa=request.empresa, ativo=True).annotate(
        estoque_atual=Sum('lotes__quantidade')
    )
    vendedores = User.objects.filter(empresa=request.empresa)

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        vendedor_id = request.POST.get('vendedor')
        observacoes = request.POST.get('observacoes', '')
        produtos_data = request.POST.getlist('produto_id')
        quantidades = request.POST.getlist('quantidade')
        precos = request.POST.getlist('preco_unitario')
        descontos = request.POST.getlist('desconto')
        subtotais = request.POST.getlist('subtotal')

        if not produtos_data:
            messages.error(request, 'Adicione pelo menos um produto.')
            return render(request, 'vendas/dav_form.html', {
                'dav': dav,
                'produtos': produtos_qs,
                'clientes': clientes,
                'vendedores': vendedores,
            })

        dav.cliente_id = cliente_id or None
        dav.vendedor_id = vendedor_id or None
        dav.observacoes = observacoes

        dav.itens.all().delete()

        total_produtos = 0
        total_descontos = 0
        total_geral = 0

        for i in range(len(produtos_data)):
            if not produtos_data[i] or not quantidades[i]:
                continue
            qtd = Decimal(quantidades[i].replace(',', '.'))
            preco = Decimal(precos[i].replace(',', '.'))
            desc = Decimal(descontos[i].replace(',', '.')) if descontos[i] else Decimal('0')
            sub = Decimal(subtotais[i].replace(',', '.')) if subtotais[i] else (qtd * preco - desc)

            ItemDAV.objects.create(
                dav=dav,
                produto_id=produtos_data[i],
                quantidade=qtd,
                preco_unitario=preco,
                desconto=desc,
                subtotal=sub,
            )
            total_produtos += qtd * preco
            total_descontos += desc
            total_geral += sub

        dav.total_produtos = total_produtos
        dav.total_descontos = total_descontos
        dav.total_geral = total_geral
        dav.save()

        messages.success(request, f'DAV {dav.numero} atualizado com sucesso.')
        return redirect('vendas:dav_detalhe', pk=dav.pk)

    context = {
        'dav': dav,
        'produtos': produtos_qs,
        'clientes': clientes,
        'vendedores': vendedores,
    }
    return render(request, 'vendas/dav_form.html', context)


@login_required
def dav_finalizar(request, pk):
    dav = get_object_or_404(DAV, pk=pk, empresa=request.empresa)
    if dav.status != 'aberto':
        messages.error(request, 'Apenas DAVs abertos podem ser finalizados.')
        return redirect('vendas:dav_detalhe', pk=dav.pk)

    if not dav.itens.exists():
        messages.error(request, 'DAV sem itens não pode ser finalizado.')
        return redirect('vendas:dav_detalhe', pk=dav.pk)

    from django.utils import timezone
    today = timezone.localdate()
    prefix = f'V-{today.strftime("%Y%m%d")}-'
    last_venda = Venda.objects.filter(
        empresa=request.empresa,
        numero_venda__startswith=prefix
    ).count()
    novo_num_venda = f'{prefix}{last_venda + 1:04d}'

    venda = Venda.objects.create(
        empresa=dav.empresa,
        numero_venda=novo_num_venda,
        cliente=dav.cliente,
        usuario=request.user,
        vendedor=dav.vendedor,
        subtotal=dav.total_produtos,
        desconto=dav.total_descontos,
        total=dav.total_geral,
        status='finalizada',
        observacoes=dav.observacoes,
    )

    for item in dav.itens.all():
        ItemVenda.objects.create(
            venda=venda,
            produto=item.produto,
            quantidade=int(item.quantidade),
            preco_unitario=item.preco_unitario,
            subtotal=item.subtotal,
        )

    dav.status = 'finalizado'
    dav.venda = venda
    dav.save()

    messages.success(request, f'DAV {dav.numero} finalizado. Venda #{venda.numero_venda} criada.')
    return redirect('vendas:detalhe', pk=venda.pk)


@login_required
def dav_cancelar(request, pk):
    dav = get_object_or_404(DAV, pk=pk, empresa=request.empresa)
    if dav.status != 'aberto':
        messages.error(request, 'Apenas DAVs abertos podem ser cancelados.')
        return redirect('vendas:davs')

    from usuarios.services import LiberacaoService
    auto_aprovado, solicitacao = LiberacaoService.solicitar(
        tipo='cancelar_dav', usuario=request.user,
        empresa=request.empresa, objeto=dav,
        motivo='Cancelamento manual pelo usuario',
    )

    if auto_aprovado:
        dav.status = 'cancelado'
        dav.save()
        from usuarios.models import HistoricoCancelamento
        HistoricoCancelamento.objects.create(
            empresa=request.empresa,
            tipo='dav',
            objeto_id=dav.id,
            objeto_str=str(dav),
            usuario=request.user,
            motivo='Cancelamento manual',
        )
        messages.success(request, f'DAV {dav.numero} cancelado.')
    else:
        messages.success(request, f'Solicitacao de cancelamento do DAV {dav.numero} enviada para aprovacao.')

    return redirect('vendas:davs')


@login_required
def dav_imprimir(request, pk):
    dav = get_object_or_404(DAV, pk=pk, empresa=request.empresa)
    return render(request, 'vendas/dav_imprimir.html', {'dav': dav})


@login_required
def api_produto_preco(request):
    produto_id = request.GET.get('produto_id')
    if not produto_id:
        return JsonResponse({'error': 'produto_id required'}, status=400)
    try:
        produto = Produto.objects.get(pk=produto_id, empresa=request.empresa)
    except Produto.DoesNotExist:
        return JsonResponse({'error': 'Produto nao encontrado'}, status=404)

    from django.db.models import Sum
    estoque = produto.lotes.aggregate(total=Sum('quantidade'))['total'] or 0

    return JsonResponse({
        'preco_venda': str(produto.preco_venda),
        'estoque_atual': estoque,
    })


@login_required
def api_promocoes_ativas(request):
    from datetime import date
    today = date.today()
    promos = Promocao.objects.filter(
        empresa=request.empresa,
        ativo=True,
        data_inicio__lte=today,
        data_fim__gte=today,
    )
    dados = [{
        'id': p.id,
        'nome': p.nome,
        'tipo': p.tipo,
        'percentual_desconto': str(p.percentual_desconto),
        'produto_id': p.produto_id,
        'classe_terapeutica_id': p.classe_terapeutica_id,
        'preco_promocional': str(p.preco_promocional) if p.preco_promocional else None,
        'quantidade_minima': p.quantidade_minima,
        'quantidade_cobrar': p.quantidade_cobrar,
    } for p in promos]
    return JsonResponse(dados, safe=False)
