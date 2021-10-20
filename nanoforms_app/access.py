from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db.models import Q
from django.shortcuts import resolve_url


def has_access_filter(request):
    if request.user.is_anonymous:
        return Q(public=True)
    return Q(user=request.user) | Q(public=True)


def required_login_or_public_test(request, view_func, args, kwargs):
    workflow_id = kwargs.get('workflow_id')
    if workflow_id:
        from nanoforms_app.models import Workflow
        o = Workflow.objects.get(id=workflow_id)
        return o.public or o.user == request.user or request.user.is_superuser
    # let the models validate access
    return True


def required_login_or_public_decorator(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request, view_func, args, kwargs):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


def required_login_or_public(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = required_login_or_public_decorator(
        required_login_or_public_test,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
