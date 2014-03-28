from django.utils.functional import lazy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

# Workaround for using reverse with success_url in class based generic views
# because direct usage of it throws an exception.
reverse_lazy = lambda name=None, *args : lazy(reverse, str)(name, args=args)


def get_group(name):
  return Group.objects.filter(name=name).first()


def user_has_group(user, group, superuser_skip=True):
  """
  Check if a user is in a certaing group.
  By default, the check is skippef ro superusers.
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