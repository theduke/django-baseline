from __future__ import unicode_literals

from decimal import Decimal
import datetime

from django import template

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import dateformat, dateparse

from django_baseline import html

register = template.Library()

@register.simple_tag
def countdown(name, date, description='', id='', granularity='sec', start=None, progressbar=False, progressbar_inversed=False, showpct=False):
    '''
    Create a countdown.
    '''

    end_date = dateparse.parse_datetime(date)
    end = dateformat.format(end_date, 'U')

    content = '<div class="name">' + name + '</div>'
    content += '<div class="description">' + description + '</div>'

    if progressbar:
        if not end: raise Exception('For progressbar, start date is requried.')
        start_date = dateparse.parse_datetime(start) or datetime.datetime.combine(dateparse.parse_date(start), datetime.time())
        now = datetime.datetime.now()

        pct = (now - start_date).total_seconds() / (end_date - start_date).total_seconds()
        pct = int(pct * 100)

        if progressbar_inversed: pct = 100 - pct

        # Note: the output is for bootstrap!
        bar = '<div class="progress progress-striped active">'
        bar += '<div class="progress-bar"  role="progressbar" aria-valuenow="{pct}" aria-valuemin="0" aria-valuemax="100" style="width: {pct}%">'
        bar += '<span class="sr-only">{pct}% Complete</span>'
        bar += '</div>'
        bar += '</div>'

        if showpct:
            bar += '<div class="percentage">{pct}%</div>'

        bar = bar.format(pct=pct)

        content += bar

    content += '<div class="counter"></div>'

    attr = {
    	'class': 'countdownbox',
    	'data-datetime': end,
    	'data-granularity': granularity
    }
    if id: attr['id'] = id 

    return html.tag('div', content, attr)
