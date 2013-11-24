from decimal import Decimal

from django import template

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import dateformat
from django.utils import dateparse

from utils import html

register = template.Library()

@register.simple_tag
def countdown(name, date, description='', id='', granularity='sec'):
    '''
    Create a countdown.
    '''

    end_date = dateparse.parse_datetime(date)
    end = dateformat.format(end_date, 'U')

    content = '<div class="name">' + name + '</div>'
    content += '<div class="description">' + description + '</div>'
    content += '<div class="counter"></div>'

    attr = {
    	'class': 'countdownbox',
    	'data-datetime': end,
    	'data-granularity': granularity
    }
    if id: attr['id'] = id 

    return html.tag('div', content, attr)
