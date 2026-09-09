from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notificacao


@login_required
def lista(request):
    notificacoes = Notificacao.objects.filter(
        empresa=request.empresa, usuario=request.user
    ).order_by('-criado_em')
    return render(request, 'notifications/lista.html', {'notificacoes': notificacoes})


@login_required
def marcar_lida(request, pk):
    notificacao = get_object_or_404(
        Notificacao, pk=pk, empresa=request.empresa, usuario=request.user
    )
    notificacao.lida = True
    notificacao.save()
    return redirect('notifications:lista')
