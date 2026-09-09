from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.contrib import messages
from .models import ContaPagar, ContaReceber, Lancamento


@login_required
def index(request):
    empresa = request.empresa
    total_pagar = ContaPagar.objects.filter(
        empresa=empresa, status='pendente'
    ).aggregate(total=Sum('valor'))['total'] or 0
    total_receber = ContaReceber.objects.filter(
        empresa=empresa, status='pendente'
    ).aggregate(total=Sum('valor'))['total'] or 0
    saldo = total_receber - total_pagar
    context = {
        'total_pagar': total_pagar,
        'total_receber': total_receber,
        'saldo': saldo,
    }
    return render(request, 'financeiro/index.html', context)


@login_required
def contas_pagar(request):
    empresa = request.empresa
    contas = ContaPagar.objects.filter(empresa=empresa).select_related('fornecedor')

    busca = request.GET.get('busca', '')
    status_filtro = request.GET.get('status', '')
    if busca:
        contas = contas.filter(
            Q(descricao__icontains=busca) | Q(fornecedor__nome__icontains=busca)
        )
    if status_filtro:
        contas = contas.filter(status=status_filtro)

    return render(request, 'financeiro/contas_pagar.html', {
        'contas': contas.order_by('-data_vencimento'),
        'busca': busca,
        'status_filtro': status_filtro,
    })


@login_required
def contas_receber(request):
    empresa = request.empresa
    contas = ContaReceber.objects.filter(empresa=empresa).select_related('cliente')

    busca = request.GET.get('busca', '')
    status_filtro = request.GET.get('status', '')
    if busca:
        contas = contas.filter(
            Q(descricao__icontains=busca) | Q(cliente__nome__icontains=busca)
        )
    if status_filtro:
        contas = contas.filter(status=status_filtro)

    return render(request, 'financeiro/contas_receber.html', {
        'contas': contas.order_by('-data_vencimento'),
        'busca': busca,
        'status_filtro': status_filtro,
    })


@login_required
def lancamentos(request):
    empresa = request.empresa
    lancamentos_list = Lancamento.objects.filter(empresa=empresa)

    busca = request.GET.get('busca', '')
    tipo_filtro = request.GET.get('tipo', '')
    if busca:
        lancamentos_list = lancamentos_list.filter(
            Q(descricao__icontains=busca) | Q(categoria__icontains=busca)
        )
    if tipo_filtro:
        lancamentos_list = lancamentos_list.filter(tipo=tipo_filtro)

    return render(request, 'financeiro/lancamentos.html', {
        'lancamentos': lancamentos_list.order_by('-data_lancamento'),
        'busca': busca,
        'tipo_filtro': tipo_filtro,
    })


@login_required
def lancamento_novo(request):
    if request.method == 'POST':
        Lancamento.objects.create(
            empresa=request.empresa,
            descricao=request.POST.get('descricao'),
            valor=request.POST.get('valor'),
            tipo=request.POST.get('tipo'),
            categoria=request.POST.get('categoria', ''),
            forma_pagamento=request.POST.get('forma_pagamento', ''),
            observacao=request.POST.get('observacao', ''),
        )
        messages.success(request, 'Lançamento criado com sucesso.')
        return redirect('financeiro:lancamentos')
    return render(request, 'financeiro/lancamento_form.html')


@login_required
def conta_pagar_editar(request, pk):
    conta = get_object_or_404(ContaPagar, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        conta.descricao = request.POST.get('descricao')
        conta.valor = request.POST.get('valor')
        conta.data_vencimento = request.POST.get('data_vencimento')
        conta.status = request.POST.get('status')
        conta.data_pagamento = request.POST.get('data_pagamento') or None
        conta.valor_pago = request.POST.get('valor_pago', 0)
        conta.documento = request.POST.get('documento', '')
        conta.observacoes = request.POST.get('observacoes', '')
        conta.save()
        messages.success(request, 'Conta atualizada com sucesso.')
        return redirect('financeiro:contas_pagar')
    return render(request, 'financeiro/conta_form.html', {'conta': conta, 'tipo': 'pagar'})


@login_required
def conta_receber_editar(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        conta.descricao = request.POST.get('descricao')
        conta.valor = request.POST.get('valor')
        conta.data_vencimento = request.POST.get('data_vencimento')
        conta.status = request.POST.get('status')
        conta.data_recebimento = request.POST.get('data_recebimento') or None
        conta.valor_recebido = request.POST.get('valor_recebido', 0)
        conta.save()
        messages.success(request, 'Conta atualizada com sucesso.')
        return redirect('financeiro:contas_receber')
    return render(request, 'financeiro/conta_form.html', {'conta': conta, 'tipo': 'receber'})
