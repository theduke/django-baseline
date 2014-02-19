import json

from django.shortcuts import render, render_to_response
from django.views.generic import edit
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse


class AjaxableResponseMixin(object):
    """
    Edit view (create, update) mixin that will return a json object with the
    errors instead of the rendered content.
    """

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)


    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            data = {
                'error': 'form_invalid',
                'errors': form.errors,
            }
            return self.render_to_json_response(data, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        return self.render_to_json_response({'error': ''})
        if self.request.is_ajax():
            pass
        else:
            return response


class CrispyFormAjaxResponseMixin(object):
    """
    Edit view (create, update) mixin that will, if it is an AJAX request,
    return just the rendered form(renderd by the crispy_form_raw.html template)
    instead of the full rendered output, and an json object with the new
    primary key on succes.

    Behaves normally for non-ajax requests.
    """

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)


    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            output = render_to_response('crispy_form_raw.html', {'form': form})
            return HttpResponse(output, status=400)
        else:
            return response


    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            return HttpResponse('')
        else:
            return response


class ExtraContextMixin(object):
    """
    A mixin for Djangos generic views classes that offers an additional
    member extra_context for easily passing additional context vars.
    """

    extra_context = {}


    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        context['model_name'] = self.model._meta.verbose_name.capitalize()
        context.update(self.extra_context)
        return context


class UserViewMixin(object):
    """
    This mixin alters a generic CREATE view that has a "created_by" field by
    automatically setting the user field to the current user when the form is submitted.
    The field name of the field to populate is specified by the user_field
    property and defaults to created_by.
    """

    user_field = 'created_by'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserViewMixin, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        obj = form.save(commit=False)
        setattr(obj, self.user_field, self.request.user)
        obj.save()
        self.object = obj

        return super(UserViewMixin, self).form_valid(form)


class CreateView(ExtraContextMixin, AjaxableResponseMixin, edit.CreateView):
    """CreateView that offers extra_context and a default template."""
    template_name = 'generics/create.html'


class UpdateView(ExtraContextMixin, AjaxableResponseMixin, edit.UpdateView):
    """UpdateView that offers extra_context and a default template."""
    template_name = 'generics/update.html'


class DeleteView(ExtraContextMixin, AjaxableResponseMixin, edit.DeleteView):
    """DeleteView that offers extra_context and a default template."""
    template_name = 'generics/delete.html'




