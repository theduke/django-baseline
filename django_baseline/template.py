from __future__ import unicode_literals

from django import template

def render_template(tpl, context):
	'''
	A shortcut function to render a partial template with context and return 
	the output.
	'''

	templates = [tpl] if type(tpl) != list else tpl
	tpl_instance = None

	for tpl in templates:
		try:
			tpl_instance = template.loader.get_template(tpl)
			break
		except template.TemplateDoesNotExist:
			pass
	
	if not tpl_instance:
		raise Exception('Template does not exist: ' + templates[-1])

	return tpl_instance.render(template.Context(context))
