from __future__ import unicode_literals

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

def group_required(group,
                   login_url=None,
                   redirect_field_name=REDIRECT_FIELD_NAME,
                   skip_superuser=True):
    """
	View decorator for requiring a user group.
	"""
    def decorator(view_func):
        @login_required(redirect_field_name=redirect_field_name,
                        login_url=login_url)
        def _wrapped_view(request, *args, **kwargs):

            if not (request.user.is_superuser and skip_superuser):
                if request.user.groups.filter(name=group).count() == 0:
                	raise PermissionDenied

            return view_func(request, *args, **kwargs)
        return _wrapped_view
        
    return decorator
