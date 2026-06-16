from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('custom_admin:login')
        if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'):
            messages.error(request, 'You do not have admin permissions.')
            return redirect('custom_admin:login')
        return view_func(request, *args, **kwargs)
    return wrapper
