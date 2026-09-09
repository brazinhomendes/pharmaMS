from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_master_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if request.user.perfil != 'admin_master':
            messages.error(request, 'Acesso restrito a administradores do sistema.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
