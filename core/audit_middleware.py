import json
from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    PATHS_TO_IGNORE = [
        '/static/',
        '/media/',
        '/favicon.ico',
        '/admin/jsi18n/',
    ]

    def process_request(self, request):
        request._audit_ip = self._get_client_ip(request)
        request._audit_ua = request.META.get('HTTP_USER_AGENT', '')[:500]

    def process_response(self, request, response):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response

        path = request.path
        if any(path.startswith(p) for p in self.PATHS_TO_IGNORE):
            return response

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return response

        try:
            self._log_action(request, response)
        except Exception:
            pass

        return response

    def _log_action(self, request, response):
        from core.audit_models import AuditLog

        acao = self._mapear_acao(request)
        if not acao:
            return

        descricao = f'{request.method} {request.path}'
        if response.status_code >= 400:
            descricao += f' [{response.status_code}]'

        AuditLog.objects.create(
            usuario=request.user,
            empresa=getattr(request, 'empresa', None),
            acao=acao,
            descricao=descricao,
            ip_address=getattr(request, '_audit_ip', None),
            user_agent=getattr(request, '_audit_ua', ''),
        )

    def _mapear_acao(self, request):
        method = request.method
        path = request.path.lower()

        if 'login' in path and method == 'POST':
            return 'login'
        if 'logout' in path:
            return 'logout'
        if 'nfe' in path or 'nfce' in path:
            if method == 'POST':
                return 'emit_nfe' if 'nfe' in path else 'emit_nfce'
        if 'caixa' in path and 'abrir' in path:
            return 'open_cash'
        if 'caixa' in path and 'fechar' in path:
            return 'close_cash'
        if 'finalizar-venda' in path:
            return 'sale'
        if 'aprovar' in path:
            return 'approve'
        if 'rejeitar' in path:
            return 'reject'
        if 'cancelar' in path or 'cancelamento' in path:
            return 'cancel'

        if method == 'POST':
            return 'create'
        if method in ('PUT', 'PATCH'):
            return 'update'
        if method == 'DELETE':
            return 'delete'

        return None

    def _get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
