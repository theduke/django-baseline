
from django import template

def render_template(tpl_name, context):
	'''
	A shortcut function to render a partial template with context and return 
	the output.
	'''
	t = template.loader.get_template(tpl_name)
	return t.render(template.Context(context))
