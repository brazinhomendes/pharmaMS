import json
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count, Max
from django.utils import timezone
from .models import Entrega
from cadastros.models import Cliente


@login_required
def lista(request):
    hoje = date.today()
    entregas = Entrega.objects.filter(empresa=request.empresa)

    status = request.GET.get('status')
    periodo = request.GET.get('periodo', 'todas')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    busca = request.GET.get('busca')

    if status and status != 'None':
        entregas = entregas.filter(status=status)

    if busca:
        entregas = entregas.filter(
            Q(cliente__nome__icontains=busca) |
            Q(endereco_entrega__icontains=busca) |
            Q(bairro__icontains=busca) |
            Q(contato_telefone__icontains=busca)
        )

    if data_inicio and data_fim:
        entregas = entregas.filter(criado_em__date__gte=data_inicio, criado_em__date__lte=data_fim)
    elif periodo == 'hoje':
        entregas = entregas.filter(criado_em__date=hoje)
    elif periodo == 'semana':
        entregas = entregas.filter(criado_em__date__gte=hoje - timedelta(days=7))
    elif periodo == 'mes':
        entregas = entregas.filter(criado_em__month=hoje.month, criado_em__year=hoje.year)

    base = Entrega.objects.filter(empresa=request.empresa)
    total_hoje = base.filter(criado_em__date=hoje).count()
    pendentes = base.filter(status='pendente').count()
    em_rota = base.filter(status='em_rota').count()
    concluidas_hoje = base.filter(status='entregue', status_entregue_em__date=hoje).count()

    context = {
        'entregas': entregas.order_by('-criado_em'),
        'status_atual': status,
        'periodo_atual': periodo,
        'data_inicio': data_inicio or '',
        'data_fim': data_fim or '',
        'busca': busca or '',
        'total_hoje': total_hoje,
        'pendentes': pendentes,
        'em_rota': em_rota,
        'concluidas_hoje': concluidas_hoje,
    }
    return render(request, 'delivery/lista.html', context)


@login_required
def novo(request):
    from decimal import Decimal
    from vendas.models import Venda, ItemVenda
    from django.db import transaction

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        taxa_entrega = Decimal(request.POST.get('taxa_entrega', 0) or 0)
        cart_json = request.POST.get('cart_items', '[]')

        with transaction.atomic():
            venda = None
            cart_items = json.loads(cart_json) if cart_json else []

            if cart_items:
                ultimo = Venda.objects.filter(empresa=request.empresa).aggregate(
                    max_num=Max('numero_venda')
                )['max_num']
                novo_numero = str(int(ultimo) + 1) if ultimo else '1'

                subtotal = sum(Decimal(str(i['preco'])) * i['qtd'] for i in cart_items)
                forma_pagamento = request.POST.get('forma_pagamento', 'dinheiro')
                valor_recebido = Decimal(request.POST.get('valor_recebido', 0) or 0)
                total_venda = subtotal + taxa_entrega
                troco = Decimal('0')
                if valor_recebido > total_venda:
                    troco = valor_recebido - total_venda

                venda = Venda.objects.create(
                    empresa=request.empresa,
                    cliente_id=cliente_id or None,
                    numero_venda=novo_numero,
                    forma_pagamento=forma_pagamento,
                    subtotal=subtotal,
                    desconto=Decimal('0'),
                    total=total_venda,
                    valor_recebido=valor_recebido,
                    troco=troco,
                    status='finalizada',
                    usuario=request.user,
                    observacoes='Venda via Delivery',
                )

                for item in cart_items:
                    ItemVenda.objects.create(
                        venda=venda,
                        produto_id=item['id'],
                        quantidade=item['qtd'],
                        preco_unitario=item['preco'],
                        subtotal=Decimal(str(item['preco'])) * item['qtd'],
                    )

            entregador_id = request.POST.get('entregador')

            entrega = Entrega(empresa=request.empresa)
            if cliente_id:
                entrega.cliente_id = cliente_id
            if venda:
                entrega.venda = venda
            if entregador_id:
                entrega.entregador_id = entregador_id
            entrega.endereco_entrega = request.POST.get('endereco_entrega', '')
            entrega.complemento = request.POST.get('complemento', '')
            entrega.bairro = request.POST.get('bairro', '')
            entrega.cidade = request.POST.get('cidade', '')
            entrega.contato_telefone = request.POST.get('contato_telefone', '')
            entrega.observacoes = request.POST.get('observacoes', '')
            entrega.taxa_entrega = taxa_entrega
            data_entrega = request.POST.get('data_entrega')
            if data_entrega:
                entrega.data_entrega = data_entrega
            if entregador_id:
                entrega.status = 'atribuido'
                entrega.status_atribuido_em = timezone.now()
            else:
                entrega.status = 'pendente'
                entrega.status_pendente_em = timezone.now()
            entrega.save()

        messages.success(request, 'Entrega cadastrada com sucesso.')
        return redirect('delivery:detalhe', pk=entrega.pk)

    cliente_id = request.GET.get('cliente_id')
    cliente = None
    if cliente_id:
        cliente = get_object_or_404(Cliente, pk=cliente_id, empresa=request.empresa)
    entregadores = get_user_model().objects.filter(
        empresa_ativa=request.empresa, perfil='entregador', is_active=True
    )
    return render(request, 'delivery/form.html', {'cliente': cliente, 'entregadores': entregadores})


@login_required
def detalhe(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk, empresa=request.empresa)
    timeline = []
    for st, label in Entrega.STATUS_CHOICES:
        ts = getattr(entrega, f'status_{st}_em', None)
        if ts:
            timeline.append({'status': st, 'label': label, 'timestamp': ts})
    timeline.sort(key=lambda x: x['timestamp'])

    status_flow = ['pendente', 'atribuido', 'em_rota', 'entregue']
    current_idx = status_flow.index(entrega.status) if entrega.status in status_flow else -1
    next_statuses = []
    if entrega.status == 'pendente':
        next_statuses = [('atribuido', 'Atribuir Entregador')]
    elif entrega.status == 'atribuido':
        next_statuses = [('em_rota', 'Iniciar Rota')]
    elif entrega.status == 'em_rota':
        next_statuses = [('entregue', 'Confirmar Entrega')]
    if entrega.status not in ('entregue', 'cancelada'):
        next_statuses.append(('cancelada', 'Cancelar Entrega'))

    context = {
        'entrega': entrega,
        'timeline': timeline,
        'next_statuses': next_statuses,
    }
    return render(request, 'delivery/detalhe.html', context)


@login_required
def atualizar_status(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    entrega = get_object_or_404(Entrega, pk=pk, empresa=request.empresa)
    novo_status = request.POST.get('status')
    if novo_status not in dict(Entrega.STATUS_CHOICES):
        messages.error(request, 'Status inválido.')
        return redirect('delivery:detalhe', pk=pk)

    valid_transitions = {
        'pendente': ['atribuido', 'cancelada'],
        'atribuido': ['em_rota', 'cancelada'],
        'em_rota': ['entregue', 'cancelada'],
        'entregue': [],
        'cancelada': [],
    }
    if novo_status not in valid_transitions.get(entrega.status, []):
        messages.error(request, f'Não é possível mudar de "{entrega.get_status_display()}" para "{dict(Entrega.STATUS_CHOICES)[novo_status]}".')
        return redirect('delivery:detalhe', pk=pk)

    entregador_id = request.POST.get('entregador')
    if novo_status == 'atribuido' and entregador_id:
        entrega.entregador_id = entregador_id

    entrega.salvar_timestamp_status(novo_status)
    messages.success(request, f'Status alterado para "{dict(Entrega.STATUS_CHOICES)[novo_status]}".')
    return redirect('delivery:detalhe', pk=pk)


@login_required
def api_buscar_cliente(request):
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
    clientes = Cliente.objects.filter(
        empresa=request.empresa
    ).filter(
        Q(nome__icontains=q) | Q(cpf_cnpj__icontains=q) | Q(telefone__icontains=q) | Q(celular__icontains=q)
    )[:20]
    data = [{
        'id': c.id,
        'nome': c.nome,
        'cpf_cnpj': c.cpf_cnpj,
        'endereco': c.endereco,
        'bairro': c.bairro,
        'cidade': c.cidade,
        'telefone': c.telefone or c.celular,
    } for c in clientes]
    return JsonResponse(data, safe=False)
