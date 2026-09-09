from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, SolicitacaoLiberacao, HistoricoCancelamento, tem_perfil_aprovador
from .forms import UsuarioForm
from .services import LiberacaoService


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.empresa_ativa_id:
                request.session['empresa_id'] = user.empresa_ativa_id
            return redirect('core:dashboard')
        return render(request, 'usuarios/login.html', {'error': 'Usuário ou senha inválidos'})
    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


@login_required
def lista(request):
    usuarios = Usuario.objects.filter(empresa_ativa=request.user.empresa_ativa)
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
def novo(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.empresa_ativa = request.user.empresa_ativa
            user.save()
            return redirect('usuarios:lista')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form.html', {'form': form})


@login_required
def editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk, empresa_ativa=request.user.empresa_ativa)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/form.html', {'form': form})


@login_required
def liberacoes(request):
    qs = SolicitacaoLiberacao.objects.filter(empresa=request.empresa)
    status = request.GET.get('status')
    tipo = request.GET.get('tipo')
    if status:
        qs = qs.filter(status=status)
    if tipo:
        qs = qs.filter(tipo=tipo)
    context = {
        'liberacoes': qs,
        'status_atual': status,
        'tipo_atual': tipo,
        'TIPO_CHOICES': SolicitacaoLiberacao.TIPO_CHOICES,
        'STATUS_CHOICES': SolicitacaoLiberacao.STATUS_CHOICES,
    }
    return render(request, 'usuarios/liberacoes.html', context)


@login_required
def liberacao_solicitar(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        motivo = request.POST.get('motivo', '')
        venda_id = request.POST.get('venda_id')
        objeto = None
        if venda_id:
            from vendas.models import Venda
            objeto = get_object_or_404(Venda, pk=venda_id, empresa=request.empresa)

        auto_aprovado, solicitacao = LiberacaoService.solicitar(
            tipo=tipo, usuario=request.user,
            empresa=request.empresa, objeto=objeto, motivo=motivo,
        )

        if auto_aprovado:
            messages.success(request, 'Operacao autorizada automaticamente.')
        else:
            messages.success(request, 'Solicitacao de liberacao enviada.')

        return redirect('usuarios:liberacoes')

    vendas = None
    from vendas.models import Venda
    vendas = Venda.objects.filter(empresa=request.empresa).order_by('-data_venda')[:50]
    return render(request, 'usuarios/liberacao_form.html', {
        'vendas': vendas,
        'TIPO_CHOICES': SolicitacaoLiberacao.TIPO_CHOICES,
    })


@login_required
def liberacao_aprovar(request, pk):
    solicitacao = get_object_or_404(
        SolicitacaoLiberacao, pk=pk, empresa=request.empresa
    )
    if solicitacao.status != 'pendente':
        messages.error(request, 'Esta solicitacao ja foi processada.')
        return redirect('usuarios:liberacoes_pendentes')

    if not tem_perfil_aprovador(request.user):
        messages.error(request, 'Voce nao tem perfil de aprovador.')
        return redirect('usuarios:liberacoes_pendentes')

    LiberacaoService.aprovar(solicitacao, request.user)
    messages.success(request, f'Solicitacao {solicitacao.tipo} aprovada.')
    return redirect('usuarios:liberacoes_pendentes')


@login_required
def liberacao_rejeitar(request, pk):
    solicitacao = get_object_or_404(
        SolicitacaoLiberacao, pk=pk, empresa=request.empresa
    )
    if solicitacao.status != 'pendente':
        messages.error(request, 'Esta solicitacao ja foi processada.')
        return redirect('usuarios:liberacoes_pendentes')

    if not tem_perfil_aprovador(request.user):
        messages.error(request, 'Voce nao tem perfil de aprovador.')
        return redirect('usuarios:liberacoes_pendentes')

    observacao = request.POST.get('observacao', '')
    LiberacaoService.rejeitar(solicitacao, request.user, observacao)
    messages.success(request, f'Solicitacao {solicitacao.tipo} rejeitada.')
    return redirect('usuarios:liberacoes_pendentes')


@login_required
def liberacoes_pendentes(request):
    qs = SolicitacaoLiberacao.objects.filter(
        empresa=request.empresa, status='pendente'
    )
    return render(request, 'usuarios/liberacoes_pendentes.html', {
        'liberacoes': qs,
    })


@login_required
def cancelamentos(request):
    historico = HistoricoCancelamento.objects.filter(empresa=request.empresa)
    return render(request, 'usuarios/cancelamentos.html', {
        'cancelamentos': historico,
    })
