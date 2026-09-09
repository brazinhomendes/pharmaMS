from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from datetime import date
from .models import Lote, MovimentoEstoque
from cadastros.models import Produto, Fornecedor


@login_required
def index(request):
    empresa = request.empresa
    lotes = Lote.objects.filter(empresa=empresa, ativo=True)
    movimentos = MovimentoEstoque.objects.filter(empresa=empresa)[:10]
    total_produtos = Produto.objects.filter(empresa=empresa, ativo=True).count()
    total_lotes = lotes.count()
    lotes_proximos = lotes.filter(data_validade__gte=date.today(), data_validade__lte=date(9999, 12, 31)).order_by('data_validade')[:5]
    lotes_vencidos = lotes.filter(data_validade__lt=date.today()).count()
    context = {
        'total_produtos': total_produtos,
        'total_lotes': total_lotes,
        'lotes_proximos': lotes_proximos,
        'lotes_vencidos': lotes_vencidos,
        'movimentos': movimentos,
    }
    return render(request, 'estoque/index.html', context)


@login_required
def lotes(request):
    empresa = request.empresa
    lotes_list = Lote.objects.filter(empresa=empresa).select_related('produto', 'fornecedor')
    return render(request, 'estoque/lotes.html', {'lotes': lotes_list})


@login_required
def lote_novo(request):
    empresa = request.empresa
    if request.method == 'POST':
        produto_id = request.POST.get('produto')
        codigo_lote = request.POST.get('codigo_lote')
        data_fabricacao = request.POST.get('data_fabricacao') or None
        data_validade = request.POST.get('data_validade')
        quantidade = request.POST.get('quantidade', 0)
        preco_custo = request.POST.get('preco_custo', 0)
        fornecedor_id = request.POST.get('fornecedor') or None
        nota_fiscal = request.POST.get('nota_fiscal', '')
        produto = get_object_or_404(Produto, pk=produto_id, empresa=empresa)
        Lote.objects.create(
            empresa=empresa,
            produto=produto,
            codigo_lote=codigo_lote,
            data_fabricacao=data_fabricacao,
            data_validade=data_validade,
            quantidade=quantidade,
            preco_custo=preco_custo,
            fornecedor_id=fornecedor_id,
            nota_fiscal=nota_fiscal,
        )
        messages.success(request, 'Lote cadastrado com sucesso.')
        return redirect('estoque:lotes')
    produtos = Produto.objects.filter(empresa=empresa, ativo=True)
    fornecedores = Fornecedor.objects.filter(empresa=empresa, ativo=True)
    return render(request, 'estoque/lote_form.html', {'produtos': produtos, 'fornecedores': fornecedores})


@login_required
def movimentos(request):
    empresa = request.empresa
    movimentos_list = MovimentoEstoque.objects.filter(empresa=empresa).select_related('produto', 'lote', 'usuario')
    return render(request, 'estoque/movimentos.html', {'movimentos': movimentos_list})


@login_required
def api_lotes_produto(request, pk):
    empresa = request.empresa
    lotes_list = Lote.objects.filter(
        empresa=empresa, produto_id=pk, ativo=True, quantidade__gt=0
    ).values('id', 'codigo_lote', 'quantidade', 'data_validade', 'preco_custo')
    return JsonResponse(list(lotes_list), safe=False)
