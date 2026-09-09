from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from empresas.models import Empresa
from configuracoes.models import ConfiguracaoSistema, ConfigFiscalSistema
from cadastros.models import Produto, Cliente, Fornecedor


@login_required
def onboarding(request):
    user = request.user

    empresa_count = Empresa.objects.count()
    produto_count = Produto.objects.filter(empresa=user.empresa_ativa).count() if user.empresa_ativa else 0
    cliente_count = Cliente.objects.filter(empresa=user.empresa_ativa).count() if user.empresa_ativa else 0

    steps = [
        {'id': 1, 'titulo': 'Dados da Empresa', 'icone': 'bi-building', 'ok': empresa_count > 0},
        {'id': 2, 'titulo': 'Configuracao Fiscal', 'icone': 'bi-receipt', 'ok': ConfigFiscalSistema.objects.filter(empresa=user.empresa_ativa).exists()},
        {'id': 3, 'titulo': 'Cadastrar Produtos', 'icone': 'bi-capsule', 'ok': produto_count > 0},
        {'id': 4, 'titulo': 'Cadastrar Clientes', 'icone': 'bi-people', 'ok': cliente_count > 0},
        {'id': 5, 'titulo': 'Abrir Caixa', 'icone': 'bi-cash-stack', 'ok': False},
    ]

    completed = sum(1 for s in steps if s['ok'])
    percent = int((completed / len(steps)) * 100)

    return render(request, 'core/onboarding.html', {
        'steps': steps,
        'completed': completed,
        'total': len(steps),
        'percent': percent,
    })


@login_required
def onboarding_empresa(request):
    if request.method == 'POST':
        empresa = Empresa.objects.create(
            nome=request.POST.get('nome', ''),
            cnpj=request.POST.get('cnpj', ''),
            ie=request.POST.get('ie', ''),
            endereco=request.POST.get('endereco', ''),
            bairro=request.POST.get('bairro', ''),
            cidade=request.POST.get('cidade', ''),
            uf=request.POST.get('uf', ''),
            cep=request.POST.get('cep', ''),
            telefone=request.POST.get('telefone', ''),
            email=request.POST.get('email', ''),
        )
        if not request.user.empresa_ativa:
            request.user.empresa_ativa = empresa
            request.user.save()
        request.session['empresa_id'] = empresa.pk

        ConfiguracaoSistema.objects.get_or_create(empresa=empresa)
        ConfigFiscalSistema.objects.get_or_create(empresa=empresa)

        messages.success(request, 'Empresa cadastrada com sucesso!')
        return redirect('core:onboarding')
    return render(request, 'core/onboarding_empresa.html')
