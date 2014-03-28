from __future__ import unicode_literals

from decimal import Decimal
import urllib

from django import template
from django.db.models import Model
from django.forms import ModelForm

from django.conf import settings
from django.core.urlresolvers import reverse

from django_baseline import html

register = template.Library()


@register.simple_tag
def table(rows):
    '''
    Output a simple table with several columns.
    '''

    output = '<table>'

    for row in rows:
        output += '<tr>'
        for column in row:
            output += '<td>{s}</td>'.format(s=column)
        output += '</tr>'

    output += '</table>'

    return output

@register.simple_tag
def link(url, text='', classes='', target='', get="", **kwargs):
    '''
    Output a link tag.
    '''

    if not (url.startswith('http') or url.startswith('/')):
        # Handle additional reverse args.
        urlargs = {}

        for arg, val in kwargs.items():
            if arg[:4] == "url_":
                urlargs[arg[4:]] = val

        url = reverse(url, kwargs=urlargs)
        if get:
            url += '?' + get

    return html.tag('a', text or url, {'class': classes, 'target': target, 'href': url})


@register.simple_tag
def jsfile(url):
    '''
    Output a script tag to a js file.
    '''

    if not url.startswith('http://') and not url[:1] == '/':
        #add media_url for relative paths
        url = settings.STATIC_URL + url

    return '<script type="text/javascript" src="{src}"></script>'.format(src=url)


@register.simple_tag
def cssfile(url):
    '''
    Output a link tag to a css stylesheet.
    '''

    if not url.startswith('http://') and not url[:1] == '/':
        #add media_url for relative paths
        url = settings.STATIC_URL + url

    return '<link href="{src}" rel="stylesheet">'.format(src=url)


@register.simple_tag
def img(url, alt='', classes='', style=''):
    '''
    Image tag helper.
    '''

    if not url.startswith('http://') and not url[:1] == '/':
        #add media_url for relative paths
        url = settings.STATIC_URL + url

    attr = {
        'class': classes,
        'alt': alt,
        'style': style,
        'src': url
    }

    return html.tag('img', '', attr)


def valid_numeric(arg):
    if isinstance(arg, (int, float, Decimal)):
        return arg
    try:
        return int(arg)
    except ValueError:
        return float(arg)


@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return valid_numeric(value) - valid_numeric(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ''
sub.is_safe = False


@register.filter
def mul(value, arg):
    """Multiply the arg with the value."""
    try:
        return valid_numeric(value) * valid_numeric(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except Exception:
            return ''
mul.is_safe = False


@register.filter
def div(value, arg):
    """Divide the arg by the value."""
    try:
        return valid_numeric(value) / valid_numeric(arg)
    except (ValueError, TypeError):
        try:
            return value / arg
        except Exception:
            return ''
div.is_safe = False


@register.filter(name='abs')
def absolute(value):
    """Return the absolute value."""
    try:
        return abs(valid_numeric(value))
    except (ValueError, TypeError):
        try:
            return abs(value)
        except Exception:
            return ''
absolute.is_safe = False


@register.filter
def mod(value, arg):
    """Return the modulo value."""
    try:
        return valid_numeric(value) % valid_numeric(arg)
    except (ValueError, TypeError):
        try:
            return value % arg
        except Exception:
            return ''
mod.is_safe = False


# Model related.

@register.filter
def model_verbose(obj, capitalize=True):
    """
    Return the verbose name of a model.
    The obj argument can be either a Model instance, or a ModelForm instance.
    This allows to retrieve the verbose name of the model of a ModelForm
    easily, without adding extra context vars.
    """

    if isinstance(obj, ModelForm):
        name = obj._meta.model._meta.verbose_name
    elif isinstance(obj,  Model):
        name = obj._meta.verbose_name
    else:
        raise Exception('Unhandled type: ' + type(obj))

    return name.capitalize() if capitalize else name
model_verbose.is_safe = False


@register.filter
def user_can_edit(obj, user):
    """
    If a model implements the user_can_edit method,
    this filter returns the result of the method.
    """

    return obj.user_can_edit(user) if hasattr(obj, "user_can_edit") else None
