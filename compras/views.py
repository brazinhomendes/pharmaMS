from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import PedidoCompra, ItemPedidoCompra, NotaFiscalEntrada, SugestaoCompra, ItemSugestaoCompra
from cadastros.models import Produto, Fornecedor
from estoque.models import Lote, MovimentoEstoque
from .services import SugestaoCompraService


@login_required
def lista(request):
    empresa = request.empresa
    pedidos = PedidoCompra.objects.filter(empresa=empresa).select_related('fornecedor')
    return render(request, 'compras/lista.html', {'pedidos': pedidos})


@login_required
def novo(request):
    empresa = request.empresa
    if request.method == 'POST':
        fornecedor_id = request.POST.get('fornecedor')
        data_previsao = request.POST.get('data_previsao') or None
        observacoes = request.POST.get('observacoes', '')
        fornecedor = get_object_or_404(Fornecedor, pk=fornecedor_id, empresa=empresa)
        ultimo = PedidoCompra.objects.filter(empresa=empresa).count()
        numero_pedido = f'PC-{ultimo + 1:04d}'
        pedido = PedidoCompra.objects.create(
            empresa=empresa,
            numero_pedido=numero_pedido,
            fornecedor=fornecedor,
            data_previsao=data_previsao,
            observacoes=observacoes,
            usuario=request.user,
        )
        produtos_ids = request.POST.getlist('produto')
        quantidades = request.POST.getlist('quantidade')
        precos = request.POST.getlist('preco_unitario')
        for pid, qtd, preco in zip(produtos_ids, quantidades, precos):
            if pid and qtd and preco:
                produto = Produto.objects.get(pk=pid, empresa=empresa)
                ItemPedidoCompra.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=int(qtd),
                    preco_unitario=preco,
                )
        messages.success(request, f'Pedido {numero_pedido} criado com sucesso.')
        return redirect('compras:detalhe', pk=pedido.pk)
    fornecedores = Fornecedor.objects.filter(empresa=empresa, ativo=True)
    produtos = Produto.objects.filter(empresa=empresa, ativo=True)
    return render(request, 'compras/form.html', {
        'fornecedores': fornecedores,
        'produtos': produtos,
    })


@login_required
def detalhe(request, pk):
    empresa = request.empresa
    pedido = get_object_or_404(
        PedidoCompra.objects.prefetch_related('itens__produto'),
        pk=pk, empresa=empresa
    )
    return render(request, 'compras/detalhe.html', {'pedido': pedido})


@login_required
def receber(request, pk):
    empresa = request.empresa
    pedido = get_object_or_404(PedidoCompra.objects.prefetch_related('itens__produto'), pk=pk, empresa=empresa)
    if request.method == 'POST':
        for item in pedido.itens.all():
            qtd_recebida = int(request.POST.get(f'qtd_recebida_{item.id}', 0))
            if qtd_recebida > 0:
                data_validade = request.POST.get(f'data_validade_{item.id}')
                codigo_lote = request.POST.get(f'codigo_lote_{item.id}', f'LOTE-{item.id}')
                if item.quantidade_recebida + qtd_recebida > item.quantidade:
                    messages.error(request, f'Quantidade recebida para {item.produto.nome} excede o pedido.')
                    return redirect('compras:receber', pk=pk)
                lote = Lote.objects.create(
                    empresa=empresa,
                    produto=item.produto,
                    codigo_lote=codigo_lote,
                    data_validade=data_validade or date.today(),
                    quantidade=qtd_recebida,
                    preco_custo=item.preco_unitario,
                )
                MovimentoEstoque.objects.create(
                    empresa=empresa,
                    produto=item.produto,
                    lote=lote,
                    tipo='entrada',
                    quantidade=qtd_recebida,
                    saldo_anterior=0,
                    saldo_posterior=qtd_recebida,
                    documento=pedido.numero_pedido,
                    usuario=request.user,
                )
                item.quantidade_recebida += qtd_recebida
                item.save()
        todos_recebidos = all(
            item.quantidade_recebida >= item.quantidade for item in pedido.itens.all()
        )
        if todos_recebidos:
            pedido.status = 'recebido'
        else:
            pedido.status = 'parcial'
        pedido.save()
        messages.success(request, 'Itens recebidos com sucesso.')
        return redirect('compras:detalhe', pk=pk)
    return render(request, 'compras/receber.html', {'pedido': pedido})


@login_required
def nf_entrada_lista(request):
    empresa = request.empresa
    nfs = NotaFiscalEntrada.objects.filter(empresa=empresa).select_related('fornecedor', 'pedido')
    return render(request, 'compras/nf_entrada_lista.html', {'nfs': nfs})


@login_required
def sugestoes(request):
    empresa = request.empresa
    sugestoes_list = SugestaoCompra.objects.filter(empresa=empresa).prefetch_related('itens')
    return render(request, 'compras/sugestoes.html', {'sugestoes': sugestoes_list})


@login_required
def sugestoes_gerar(request):
    empresa = request.empresa
    if request.method == 'POST':
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        apenas_curva_a = request.POST.get('apenas_curva_a') == 'on'
        if not data_inicio or not data_fim:
            messages.error(request, 'Informe o período de análise.')
            return render(request, 'compras/sugestoes_gerar.html')
        data_inicio = date.fromisoformat(data_inicio)
        data_fim = date.fromisoformat(data_fim)
        sugestao = SugestaoCompraService.gerar_sugestoes(empresa, data_inicio, data_fim, apenas_curva_a)
        messages.success(request, f'Sugestão gerada com {sugestao.itens.count()} itens.')
        return redirect('compras:sugestao_detalhe', pk=sugestao.pk)
    return render(request, 'compras/sugestoes_gerar.html')


@login_required
def sugestao_detalhe(request, pk):
    empresa = request.empresa
    sugestao = get_object_or_404(
        SugestaoCompra.objects.prefetch_related('itens__produto'),
        pk=pk, empresa=empresa
    )
    return render(request, 'compras/sugestao_detalhe.html', {'sugestao': sugestao})


@login_required
def sugestao_aprovar_item(request, pk, item_pk):
    empresa = request.empresa
    sugestao = get_object_or_404(SugestaoCompra, pk=pk, empresa=empresa)
    item = get_object_or_404(ItemSugestaoCompra, pk=item_pk, sugestao=sugestao)
    item.aprovado = not item.aprovado
    item.save()
    messages.success(request, f'Item {item.produto.nome} {"aprovado" if item.aprovado else "desaprovado"}.')
    return redirect('compras:sugestao_detalhe', pk=pk)


@login_required
def sugestao_criar_pedido(request, pk):
    empresa = request.empresa
    sugestao = get_object_or_404(
        SugestaoCompra.objects.prefetch_related('itens__produto'),
        pk=pk, empresa=empresa
    )
    if sugestao.processada:
        messages.warning(request, 'Esta sugestão já foi processada.')
        return redirect('compras:sugestao_detalhe', pk=pk)

    itens_aprovados = sugestao.itens.filter(aprovado=True)
    if not itens_aprovados.exists():
        messages.error(request, 'Nenhum item aprovado para criar pedido.')
        return redirect('compras:sugestao_detalhe', pk=pk)

    fornecedores = {}
    for item in itens_aprovados:
        f = item.produto.laboratorio.fornecedor_set.first() if item.produto.laboratorio else None
        if f:
            fornecedores.setdefault(f, []).append(item)

    pedidos_criados = []
    for fornecedor, itens in fornecedores.items():
        ultimo = PedidoCompra.objects.filter(empresa=empresa).count()
        numero_pedido = f'PC-SUG-{ultimo + 1:04d}'
        pedido = PedidoCompra.objects.create(
            empresa=empresa,
            numero_pedido=numero_pedido,
            fornecedor=fornecedor,
            usuario=request.user,
        )
        for item in itens:
            ItemPedidoCompra.objects.create(
                pedido=pedido,
                produto=item.produto,
                quantidade=item.sugestao_compra,
                preco_unitario=item.produto.preco_custo,
            )
        pedidos_criados.append(pedido)

    sugestao.processada = True
    if pedidos_criados:
        sugestao.pedido = pedidos_criados[0]
    sugestao.save()

    messages.success(request, f'{len(pedidos_criados)} pedido(s) criado(s) a partir da sugestão.')
    return redirect('compras:sugestao_detalhe', pk=pk)
