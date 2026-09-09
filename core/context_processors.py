def empresa_atual(request):
    empresa = getattr(request, 'empresa', None)
    return {'empresa_atual': empresa}


def pending_liberacoes(request):
    count = 0
    if request.user.is_authenticated:
        from usuarios.models import SolicitacaoLiberacao
        empresa = getattr(request, 'empresa', None)
        if empresa:
            count = SolicitacaoLiberacao.objects.filter(
                empresa=empresa, status='pendente'
            ).count()
    return {'pending_liberacoes_count': count}
