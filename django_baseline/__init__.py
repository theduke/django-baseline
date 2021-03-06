"""Extended base functionality for Django framework."""

from __future__ import unicode_literals

__version__ = "0.2.2"


from django.utils.functional import lazy
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import Group
from django.conf import settings
from django.middleware import csrf


def get_or_create_csrf_token(request):
    token = request.META.get('CSRF_COOKIE', None)
    if token is None:
        token = csrf._get_new_csrf_key()
        request.META['CSRF_COOKIE'] = token
        request.META['CSRF_COOKIE_USED'] = True
    return token


def get_config(key, default=None):
    """
    Get settings from django.conf if exists,
    return default value otherwise

    example:

    ADMIN_EMAIL = get_config('ADMIN_EMAIL', 'default@email.com')
    """
    return getattr(settings, key, default)


def get_group(name):
    """
    Get a django.contrib.auth group model object by group name.
    """
    return Group.objects.filter(name=name).first()


def user_has_group(user, group, superuser_skip=True):
    """
    Check if a user is in a certaing group.
    By default, the check is skipped for superusers.
    """

    if user.is_superuser and superuser_skip:
        return True

    return user.groups.filter(name=group).exists()


def resolve_class(class_path):
    """
    Load a class by a fully qualified class_path,
    eg. myapp.models.ModelName
    """

    modulepath, classname = class_path.rsplit('.', 1)
    module = __import__(modulepath, fromlist=[classname])
    return getattr(module, classname)
