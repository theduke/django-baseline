# Various html helpers.
from __future__ import unicode_literals


def attributes(attr):
    parts = ['{k}="{v}"'.format(k=key, v=val) for key, val in attr.items()]
    return ' '.join(parts)


def tag(name, content='', attr={}, filter_empty_attr=True):
	if filter_empty_attr: attr = {k:v for k,v in attr.items() if v}
	attr = ' ' + attributes(attr) if len(attr) else ''

	return '<{n}{a}>{c}</{n}>'.format(n=name, c=content, a=attr)
