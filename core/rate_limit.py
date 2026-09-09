import time
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib.auth.views import LoginView


MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutos


class RateLimitLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path.endswith('/login/'):
            ip = self._get_client_ip(request)
            key = f'login_attempts:{ip}'
            attempts = cache.get(key, 0)

            if attempts >= MAX_LOGIN_ATTEMPTS:
                remaining = cache.ttl(key)
                if remaining <= 0:
                    cache.delete(key)
                else:
                    minutes = remaining // 60
                    seconds = remaining % 60
                    return JsonResponse({
                        'error': f'Tempo de espera: {minutes}min {seconds}s',
                        'retry_after': remaining,
                    }, status=429)

        response = self.get_response(request)

        if request.method == 'POST' and request.path.endswith('/login/'):
            ip = self._get_client_ip(request)
            key = f'login_attempts:{ip}'
            if response.status_code == 200 or (hasattr(response, 'url') and response.url):
                cache.delete(key)
            else:
                attempts = cache.get(key, 0) + 1
                cache.set(key, attempts, LOCKOUT_SECONDS)

        return response

    def _get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
