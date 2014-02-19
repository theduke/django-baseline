from django.utils.functional import lazy
from django.core.urlresolvers import reverse

# Workaround for using reverse with success_url in class based generic views
# because direct usage of it throws an exception.
reverse_lazy = lambda name=None, *args : lazy(reverse, str)(name, args=args)


def resolve_class(class_path):
    """
    Load a class by a fully qualified class_path,
    eg. myapp.models.ModelName
    """
    modulepath, classname = class_path.rsplit('.', 1)
    module = __import__(modulepath, fromlist=[classname])
    return getattr(module, classname)
