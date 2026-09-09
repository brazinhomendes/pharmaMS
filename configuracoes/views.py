from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    ConfiguracaoSistema, ConfigFiscalSistema,
    ConfiguracaoMunicipal, ConfiguracaoEmail, ConfiguracaoBackup
)


@login_required
def index(request):
    config, _ = ConfiguracaoSistema.objects.get_or_create(empresa=request.empresa)
    if request.method == 'POST':
        config.nome_sistema = request.POST.get('nome_sistema', 'pharmaMS')
        config.cor_primaria = request.POST.get('cor_primaria', '#7c3aed')
        config.cor_secundaria = request.POST.get('cor_secundaria', '#1c1917')
        config.tema_escuro = request.POST.get('tema_escuro') == 'on'
        config.moeda = request.POST.get('moeda', 'BRL')
        config.msg_pdv = request.POST.get('msg_pdv', '')
        config.save()
        messages.success(request, 'Configuracoes salvas com sucesso.')
        return redirect('configuracoes:index')
    return render(request, 'configuracoes/index.html', {'config': config})


@login_required
def fiscal(request):
    config, _ = ConfigFiscalSistema.objects.get_or_create(empresa=request.empresa)
    if request.method == 'POST':
        config.cnae = request.POST.get('cnae', '')
        config.cnes = request.POST.get('cnes', '')
        config.codigo_municipio = request.POST.get('codigo_municipio', '')
        config.inscricao_municipal = request.POST.get('inscricao_municipal', '')
        config.perfil_ecf = request.POST.get('perfil_ecf', 'A')

        config.nfe_ambiente = request.POST.get('nfe_ambiente', '2')
        config.nfe_versao = request.POST.get('nfe_versao', '4.00')
        config.nfe_serie = int(request.POST.get('nfe_serie', 1))
        config.nfe_numero_atual = int(request.POST.get('nfe_numero_atual', 0))

        config.nfce_ambiente = request.POST.get('nfce_ambiente', '2')
        config.nfce_versao = request.POST.get('nfce_versao', '4.00')
        config.nfce_serie = int(request.POST.get('nfce_serie', 1))
        config.nfce_numero_atual = int(request.POST.get('nfce_numero_atual', 0))
        config.nfce_csc_id = request.POST.get('nfce_csc_id', '')
        config.nfce_csc_token = request.POST.get('nfce_csc_token', '')
        config.nfce_csc_token = request.POST.get('nfce_csc_token', '')

        config.certificado_senha = request.POST.get('certificado_senha', '')
        if request.FILES.get('certificado_a1'):
            config.certificado_a1 = request.FILES['certificado_a1']

        config.sped_fiscal = request.POST.get('sped_fiscal') == 'on'
        config.sped_contabil = request.POST.get('sped_contabil') == 'on'
        config.sped_contribuicoes = request.POST.get('sped_contribuicoes') == 'on'
        config.sintegra = request.POST.get('sintegra') == 'on'

        config.save()
        messages.success(request, 'Configuracoes fiscais salvas.')
        return redirect('configuracoes:fiscal')
    return render(request, 'configuracoes/fiscal.html', {'config': config})


@login_required
def municipal(request):
    config, _ = ConfiguracaoMunicipal.objects.get_or_create(empresa=request.empresa)
    if request.method == 'POST':
        config.aliquota_issqn = float(request.POST.get('aliquota_issqn', 0))
        config.aliquota_pis = float(request.POST.get('aliquota_pis', 1.65))
        config.aliquota_cofins = float(request.POST.get('aliquota_cofins', 7.6))
        config.aliquota_icms_padrao = float(request.POST.get('aliquota_icms_padrao', 18))
        config.aliquota_fcp = float(request.POST.get('aliquota_fcp', 0))
        config.cnae_principal = request.POST.get('cnae_principal', '')
        config.natureza_operacao = request.POST.get('natureza_operacao', 'Venda de Mercadoria')
        config.regime_tributario = request.POST.get('regime_tributario', '1')
        config.save()
        messages.success(request, 'Configuracoes municipais salvas.')
        return redirect('configuracoes:municipal')
    return render(request, 'configuracoes/municipal.html', {'config': config})


@login_required
def email_config(request):
    config, _ = ConfiguracaoEmail.objects.get_or_create(empresa=request.empresa)
    if request.method == 'POST':
        config.smtp_host = request.POST.get('smtp_host', '')
        config.smtp_port = int(request.POST.get('smtp_port', 587))
        config.smtp_user = request.POST.get('smtp_user', '')
        config.smtp_senha = request.POST.get('smtp_senha', '')
        config.smtp_usa_tls = request.POST.get('smtp_usa_tls') == 'on'
        config.email_remetente = request.POST.get('email_remetente', '')
        config.nome_remetente = request.POST.get('nome_remetente', 'pharmaMS')
        config.save()
        messages.success(request, 'Configuracoes de email salvas.')
        return redirect('configuracoes:email')
    return render(request, 'configuracoes/email.html', {'config': config})


@login_required
def backup_config(request):
    config, _ = ConfiguracaoBackup.objects.get_or_create(empresa=request.empresa)
    if request.method == 'POST':
        config.backup_automatico = request.POST.get('backup_automatico') == 'on'
        config.backup_frequencia = request.POST.get('backup_frequencia', 'diario')
        config.backup_hora = request.POST.get('backup_hora', '02:00')
        config.backup_manter_dias = int(request.POST.get('backup_manter_dias', 30))
        config.backup_local = request.POST.get('backup_local', '/backups')
        config.save()
        messages.success(request, 'Configuracoes de backup salvas.')
        return redirect('configuracoes:backup')
    return render(request, 'configuracoes/backup.html', {'config': config})
