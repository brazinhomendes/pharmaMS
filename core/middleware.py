from django.utils.functional import SimpleLazyObject


def get_empresa_atual(request):
    if not request.user.is_authenticated:
        return None
    empresa_id = request.session.get('empresa_id')
    if not empresa_id and hasattr(request.user, 'empresa_ativa_id'):
        empresa_id = request.user.empresa_ativa_id
    if empresa_id:
        from empresas.models import Empresa
        try:
            return Empresa.objects.get(pk=empresa_id)
        except Empresa.DoesNotExist:
            return None
    return None


class EmpresaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.empresa = SimpleLazyObject(lambda: get_empresa_atual(request))
        return self.get_response(request)
