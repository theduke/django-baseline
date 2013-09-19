from decimal import Decimal

from django import template

from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def table(rows):
    output = '<table>'

    for row in rows:
        output += '<tr>'
        for column in row:
            output += '<td>{s}</td>'.format(s=column)
        output += '</tr>'

    output += '</table>'

    return output

@register.simple_tag
def link(url, text='', classes=''):
    if not (url.startswith('http') or url.startswith('/')):
        url = reverse(url)

    if not text:
        text = url
    if classes:
        classes = ' class="{cl}"'.format(cl=classes)
    return '<a href="{url}"{cl}>{text}</a>'.format(url=url, cl=classes, text=text)


@register.simple_tag
def jsfile(url):
    if not url.startswith('http://') and not url[:1] == '/':
        #add media_url for relative paths
        url = settings.STATIC_URL + url

    return '<script type="text/javascript" src="{src}"></script>'.format(src=url)


@register.simple_tag
def cssfile(url):
    if not url.startswith('http://') and not url[:1] == '/':
        #add media_url for relative paths
        url = settings.STATIC_URL + url

    return '<link href="{src}" rel="stylesheet">'.format(src=url)


@register.simple_tag
def img(url, alt='', classes=''):
    if not url.startswith('http://') and not url[:1] == '/':
        #add media_url for relative paths
        url = settings.STATIC_URL + url
    if classes:
        classes = ' class="{c}"'.format(c=classes)
    if alt:
        alt = ' alt="{alt}" title="{alt}"'.format(alt=alt)
    return '<img src="{src}"{cl}{alt}>'.format(src=url, cl=classes, alt=alt)

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
