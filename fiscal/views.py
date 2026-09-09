from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import NFe, NFCe, ConfiguracaoFiscal, SpedContribuicoes, Sintegra
from vendas.models import Venda
from .services import NFCeService, NFeService


@login_required
def index(request):
    empresa = request.empresa
    nfe_count = NFe.objects.filter(empresa=empresa).count()
    nfe_pendentes = NFe.objects.filter(empresa=empresa, status='pendente').count()
    nfce_count = NFCe.objects.filter(empresa=empresa).count()
    nfce_pendentes = NFCe.objects.filter(empresa=empresa, status_autorizacao='pendente').count()
    sped_count = SpedContribuicoes.objects.filter(empresa=empresa).count()
    sintegra_count = Sintegra.objects.filter(empresa=empresa).count()
    return render(request, 'fiscal/index.html', {
        'nfe_count': nfe_count,
        'nfe_pendentes': nfe_pendentes,
        'nfce_count': nfce_count,
        'nfce_pendentes': nfce_pendentes,
        'sped_count': sped_count,
        'sintegra_count': sintegra_count,
    })


@login_required
def nfe_lista(request):
    empresa = request.empresa
    notas = NFe.objects.filter(empresa=empresa).select_related('cliente', 'venda')
    return render(request, 'fiscal/nfe_lista.html', {'notas': notas})


@login_required
def nfe_nova(request):
    empresa = request.empresa
    if request.method == 'POST':
        venda_id = request.POST.get('venda')
        venda = get_object_or_404(Venda, pk=venda_id, empresa=empresa)
        config = ConfiguracaoFiscal.objects.filter(empresa=empresa).first()
        if not config:
            messages.error(request, 'Configure o fiscal antes de emitir NF-e.')
            return redirect('fiscal:config')
        modelo = request.POST.get('modelo', '55')
        try:
            nfe = NFeService.emitir_nfe(venda, emitente=empresa, modelo=modelo)
            messages.success(request, f'NF-e {nfe} emitida com sucesso.')
        except Exception as e:
            messages.error(request, f'Erro ao emitir NF-e: {e}')
        return redirect('fiscal:nfe_lista')
    vendas = Venda.objects.filter(empresa=empresa).order_by('-criado_em')[:50]
    return render(request, 'fiscal/nfe_form.html', {'vendas': vendas})


@login_required
def nfe_xml(request, pk):
    empresa = request.empresa
    nfe = get_object_or_404(NFe, pk=pk, empresa=empresa)
    response = HttpResponse(nfe.xml_enviado, content_type='application/xml; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="nfe-{nfe.chave_acesso}.xml"'
    return response


@login_required
def nfe_cancelar(request, pk):
    empresa = request.empresa
    nfe = get_object_or_404(NFe, pk=pk, empresa=empresa)
    if nfe.status not in ('autorizada', 'pendente'):
        messages.error(request, f'Não é possível cancelar NF-e com status {nfe.status}.')
        return redirect('fiscal:nfe_lista')

    tipo = 'cancelar_nfce' if nfe.modelo == '65' else 'cancelar_nfe'

    from usuarios.services import LiberacaoService
    auto_aprovado, solicitacao = LiberacaoService.solicitar(
        tipo=tipo, usuario=request.user,
        empresa=empresa, objeto=nfe,
        motivo='Cancelamento manual pelo usuario',
    )

    if auto_aprovado:
        nfe.status = 'cancelada'
        nfe.save()
        from usuarios.models import HistoricoCancelamento
        HistoricoCancelamento.objects.create(
            empresa=empresa,
            tipo='nfce' if nfe.modelo == '65' else 'nfe',
            objeto_id=nfe.id,
            objeto_str=str(nfe),
            usuario=request.user,
            motivo='Cancelamento manual',
        )
        messages.success(request, f'NF-e {nfe} cancelada.')
    else:
        messages.success(request, f'Solicitacao de cancelamento de {nfe} enviada para aprovacao.')

    return redirect('fiscal:nfe_lista')


@login_required
def config(request):
    empresa = request.empresa
    config_instance, created = ConfiguracaoFiscal.objects.get_or_create(
        empresa=empresa
    )
    if request.method == 'POST':
        config_instance.serie_nfe = request.POST.get('serie_nfe', 1)
        config_instance.serie_nfce = request.POST.get('serie_nfce', 1)
        config_instance.proximo_numero_nfe = request.POST.get('proximo_numero_nfe', 1)
        config_instance.proximo_numero_nfce = request.POST.get('proximo_numero_nfce', 1)
        config_instance.regime_tributario = request.POST.get('regime_tributario', '1')
        config_instance.csc = request.POST.get('csc', '')
        config_instance.csc_id = request.POST.get('csc_id', '')
        config_instance.token_ibpt = request.POST.get('token_ibpt', '')
        config_instance.save()
        messages.success(request, 'Configuração fiscal salva.')
        return redirect('fiscal:config')
    return render(request, 'fiscal/config.html', {'config': config_instance})


@login_required
def sped_lista(request):
    empresa = request.empresa
    speds = SpedContribuicoes.objects.filter(empresa=empresa)
    return render(request, 'fiscal/sped_lista.html', {'speds': speds})


@login_required
def sintegra_lista(request):
    empresa = request.empresa
    sintegras = Sintegra.objects.filter(empresa=empresa)
    return render(request, 'fiscal/sintegra_lista.html', {'sintegras': sintegras})


@login_required
def nfce_lista(request):
    empresa = request.empresa
    nfces = NFCe.objects.filter(empresa=empresa).select_related('venda', 'venda__cliente')
    status_filter = request.GET.get('status')
    if status_filter:
        nfces = nfces.filter(status_autorizacao=status_filter)
    return render(request, 'fiscal/nfce_lista.html', {'nfces': nfces})


@login_required
def nfce_pendentes(request):
    empresa = request.empresa
    nfces = NFCe.objects.filter(
        empresa=empresa, status_autorizacao='pendente'
    ).select_related('venda', 'venda__cliente')
    return render(request, 'fiscal/nfce_pendentes.html', {'nfces': nfces})


@login_required
def nfce_detalhe(request, pk):
    empresa = request.empresa
    nfce = get_object_or_404(NFCe, pk=pk, empresa=empresa)
    return render(request, 'fiscal/nfce_detalhe.html', {'nfce': nfce})


@login_required
def nfce_xml(request, pk):
    empresa = request.empresa
    nfce = get_object_or_404(NFCe, pk=pk, empresa=empresa)
    return HttpResponse(nfce.xml_enviado, content_type='application/xml; charset=utf-8')


@login_required
def nfce_danfe(request, pk):
    empresa = request.empresa
    nfce = get_object_or_404(NFCe, pk=pk, empresa=empresa)
    context = NFCeService.imprimir_danfe_nfce(nfce)
    return render(request, 'fiscal/nfce_danfe.html', context)


@login_required
def nfce_cancelar(request, pk):
    empresa = request.empresa
    nfce = get_object_or_404(NFCe, pk=pk, empresa=empresa)
    if request.method == 'POST':
        if nfce.status_autorizacao in ('pendente', 'autorizada'):
            nfce.status_autorizacao = 'cancelada'
            nfce.save(update_fields=['status_autorizacao'])
            messages.success(request, f'NFC-e {nfce.numero} cancelada.')
        else:
            messages.error(request, f'Nao e possivel cancelar NFC-e com status {nfce.status_autorizacao}.')
        return redirect('fiscal:nfce_lista')
    return redirect('fiscal:nfce_detalhe', pk=pk)


@login_required
def nfce_reemitir(request):
    empresa = request.empresa
    if request.method == 'POST':
        reemitidas = NFCeService.reemitir_pendentes(empresa)
        messages.success(request, f'{len(reemitidas)} NFC-e(s) reemitida(s) com sucesso.')
        return redirect('fiscal:nfce_pendentes')
    return redirect('fiscal:nfce_lista')
