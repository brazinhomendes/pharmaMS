from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
from .models import TemplateWhatsApp, MensagemWhatsApp, EvolutionConfig, ConversaWhatsApp
from .evolution_service import EvolutionAPIService
from .agent import AgenteWhatsApp

logger = logging.getLogger(__name__)


@login_required
def index(request):
    templates = TemplateWhatsApp.objects.filter(empresa=request.empresa)
    mensagens = MensagemWhatsApp.objects.filter(empresa=request.empresa)[:20]

    stats = {
        'total_enviadas': MensagemWhatsApp.objects.filter(
            empresa=request.empresa, status__in=['enviada', 'entregue', 'lida']
        ).count(),
        'pendentes': MensagemWhatsApp.objects.filter(
            empresa=request.empresa, status='pendente'
        ).count(),
        'erros': MensagemWhatsApp.objects.filter(
            empresa=request.empresa, status='erro'
        ).count(),
    }

    return render(request, 'whatsapp/index.html', {
        'templates': templates,
        'mensagens': mensagens,
        'stats': stats,
    })


@login_required
def template_novo(request):
    if request.method == 'POST':
        template = TemplateWhatsApp(
            empresa=request.empresa,
            nome=request.POST.get('nome', ''),
            categoria=request.POST.get('categoria', 'personalizado'),
            corpo=request.POST.get('corpo', ''),
        )
        template.save()
        messages.success(request, 'Template criado com sucesso.')
        return redirect('whatsapp:index')
    return render(request, 'whatsapp/template_form.html')


@login_required
def template_editar(request, pk):
    template = get_object_or_404(TemplateWhatsApp, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        template.nome = request.POST.get('nome', template.nome)
        template.categoria = request.POST.get('categoria', template.categoria)
        template.corpo = request.POST.get('corpo', template.corpo)
        template.ativo = 'ativo' in request.POST
        template.save()
        messages.success(request, 'Template atualizado.')
        return redirect('whatsapp:index')
    return render(request, 'whatsapp/template_form.html', {'template': template})


@login_required
def template_excluir(request, pk):
    template = get_object_or_404(TemplateWhatsApp, pk=pk, empresa=request.empresa)
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Template excluido.')
    return redirect('whatsapp:index')


@login_required
def enviar_mensagem(request):
    if request.method == 'POST':
        msg = MensagemWhatsApp(
            empresa=request.empresa,
            destinatario_nome=request.POST.get('destinatario_nome', ''),
            destinatario_telefone=request.POST.get('destinatario_telefone', ''),
            mensagem=request.POST.get('mensagem', ''),
            status='pendente',
        )
        template_id = request.POST.get('template_id')
        if template_id:
            msg.template_id = template_id
        msg.save()
        messages.success(request, 'Mensagem enfileirada para envio.')
        return redirect('whatsapp:index')

    templates = TemplateWhatsApp.objects.filter(empresa=request.empresa, ativo=True)
    return render(request, 'whatsapp/enviar.html', {'templates': templates})


@login_required
def api_status_mensagens(request):
    pendentes = MensagemWhatsApp.objects.filter(
        empresa=request.empresa, status='pendente'
    ).count()
    enviadas_hoje = MensagemWhatsApp.objects.filter(
        empresa=request.empresa, status__in=['enviada', 'entregue'],
        criado_em__date=timezone.localdate()
    ).count()
    return JsonResponse({
        'pendentes': pendentes,
        'enviadas_hoje': enviadas_hoje,
    })


@login_required
def evolution_config(request):
    config = EvolutionConfig.objects.filter(empresa=request.empresa).first()
    status_conexao = None
    qr_code = None

    if config:
        service = EvolutionAPIService(config)
        status_conexao = service.status_instancia()

        if status_conexao and status_conexao.get('state') != 'open':
            qr_data = service.conectar_instancia()
            if isinstance(qr_data, dict) and 'base64' in str(qr_data):
                qr_code = qr_data.get('base64', '')
                if not qr_code:
                    for key, val in qr_data.items():
                        if isinstance(val, str) and val.startswith('data:image'):
                            qr_code = val
                            break

    if request.method == 'POST':
        dados = {
            'nome_instancia': request.POST.get('nome_instancia', ''),
            'api_url': request.POST.get('api_url', ''),
            'api_key': request.POST.get('api_key', ''),
            'auto_responder': 'auto_responder' in request.POST,
            'mensagem_boas_vindas': request.POST.get('mensagem_boas_vindas', ''),
        }

        if config:
            for k, v in dados.items():
                setattr(config, k, v)
            config.save()
        else:
            dados['empresa'] = request.empresa
            config = EvolutionConfig.objects.create(**dados)

        messages.success(request, 'Configuracao salva com sucesso.')
        return redirect('whatsapp:evolution_config')

    return render(request, 'whatsapp/evolution_config.html', {
        'config': config,
        'status_conexao': status_conexao,
        'qr_code': qr_code,
    })


@login_required
def evolution_qrcode(request, pk):
    config = get_object_or_404(EvolutionConfig, pk=pk, empresa=request.empresa)
    service = EvolutionAPIService(config)
    resultado = service.conectar_instancia()
    return JsonResponse(resultado)


@login_required
def evolution_conectar(request, pk):
    config = get_object_or_404(EvolutionConfig, pk=pk, empresa=request.empresa)
    service = EvolutionAPIService(config)
    resultado = service.conectar_instancia()
    return JsonResponse(resultado)


@login_required
def evolution_configurar_webhook(request, pk):
    config = get_object_or_404(EvolutionConfig, pk=pk, empresa=request.empresa)
    service = EvolutionAPIService(config)

    webhook_url = request.build_absolute_uri('/whatsapp/webhook/')
    resultado = service.configurar_webhook(webhook_url)

    config.webhook_url = webhook_url
    config.save()

    messages.success(request, f'Webhook configurado: {webhook_url}')
    return redirect('whatsapp:evolution_config')


@csrf_exempt
@require_POST
def webhook_evolution(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    event = payload.get('event', '')
    instance = payload.get('instance', '')
    data = payload.get('data', {})

    logger.info(f'Webhook recebido: {event} da instancia {instance}')

    if event == 'messages.upsert':
        processar_mensagem_recebida(instance, data)

    return JsonResponse({'status': 'ok'})


def processar_mensagem_recebida(instance_name, data):
    config = EvolutionConfig.objects.filter(
        nome_instancia=instance_name, ativo=True
    ).first()
    if not config:
        return

    key = data.get('key', {})
    numero = key.get('remoteJid', '').replace('@s.whatsapp.net', '').replace('@lid', '')
    de_mim = key.get('fromMe', False)

    if de_mim:
        return

    mensagem_texto = data.get('message', {}).get('conversation', '')
    if not mensagem_texto:
        mensagem_texto = data.get('message', {}).get('extendedTextMessage', {}).get('text', '')

    if not mensagem_texto:
        return

    push_name = data.get('pushName', '')

    conversa, _ = ConversaWhatsApp.objects.get_or_create(
        empresa=config.empresa,
        telefone=numero,
        defaults={'nome': push_name}
    )
    if push_name and not conversa.nome:
        conversa.nome = push_name
        conversa.save()

    MensagemWhatsApp.objects.create(
        empresa=config.empresa,
        conversa=conversa,
        destinatario_nome=push_name,
        destinatario_telefone=numero,
        mensagem=mensagem_texto,
        direcao='recebida',
        status='recebida',
    )

    if config.auto_responder:
        service = EvolutionAPIService(config)
        agente = AgenteWhatsApp(config.empresa, conversa)
        resposta = agente.processar(mensagem_texto)

        if resposta:
            resultado = service.enviar_mensagem(numero, resposta)
            MensagemWhatsApp.objects.create(
                empresa=config.empresa,
                conversa=conversa,
                destinatario_nome=push_name,
                destinatario_telefone=numero,
                mensagem=resposta,
                mensagem_id=resultado.get('message_id', ''),
                direcao='enviada',
                status='enviada' if resultado.get('success') else 'erro',
            )
