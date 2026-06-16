from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the admin panel.')
            return redirect('accounts:login')
        if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'):
            messages.error(request, 'You do not have permission to access this area.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper
