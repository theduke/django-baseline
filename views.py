import json

from django.shortcuts import render, render_to_response
from django.views.generic import edit
from django.views.generic import detail
from django.forms.models import inlineformset_factory, modelformset_factory
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse


from .forms import CrispyFormSetHelper


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
        if self.request.is_ajax():
            return self.render_to_json_response({'error': ''})
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

        return HttpResponseRedirect(self.get_success_url())


class DetailView(detail.DetailView):

    template_name = "generics/detail.html"
    fields = None

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        fields = self.fields or self.model._meta.get_all_field_names()
        field_data = {name:getattr(self.object, name) for name in fields}

        context['fields'] = field_data

        return context


class CreateView(ExtraContextMixin, edit.CreateView):
    """CreateView that offers extra_context and a default template."""
    template_name = 'generics/create.html'


class UpdateView(ExtraContextMixin, edit.UpdateView):
    """UpdateView that offers extra_context and a default template."""
    template_name = 'generics/update.html'


class DeleteView(ExtraContextMixin, edit.DeleteView):
    """DeleteView that offers extra_context and a default template."""
    template_name = 'generics/delete.html'


class FormSetMixin(object):
    fields = None
    excluded_fields = ['created_at', 'created_by']

    # m2m fields that should be displayed with the default widget, 
    # instead of inline.
    forced_regular_fields = []

    extra = 1
    can_delete = True

    # Extra arguments for the formset factory for a field.
    factory_extra_args = {}


    def __init__(self, *args, **kwargs):
        super(FormSetMixin, self).__init__(*args, **kwargs)

        # Auto-set fields to exclude the fieldsets.
        if self.fields == None:
            # All regular fields, except explicitly excluded ones.
            self.fields = [field.name for field in self.model._meta.fields if not field.name in self.excluded_fields]
            # Also add m2m fields that are explcitly set to normal widget
            # with self.forced_regular_fields.
            self.fields += [field.name for field in self.model._meta.many_to_many if field.name in self.forced_regular_fields]            


    def get_fieldset_crispy_helper(self):
        return CrispyFormSetHelper()


    def get_context_data(self, **kwargs):
        context = super(FormSetMixin, self).get_context_data(**kwargs)
        context['fieldsets'] = self.get_fieldsets()
        context['helper'] = self.get_fieldset_crispy_helper()

        return context


    def form_valid(self, form):
        # All is valid, so save the main form, and then
        # also persist and add all the m2m objects.
        instance = self.object = form.save(commit=False)

        for name, formset in self.formsets.items():
            instances = formset.save()
            for model in instances:
                getattr(instance, name).add(model)

        instance.save()

        return HttpResponseRedirect(self.get_success_url())


    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        formsets = self.formsets = self.get_fieldsets()

        # Check if both the form and all the fieldsets are valid.
        valid = form.is_valid() and reduce(lambda x, y: x and y, [f.is_valid() for name, f in formsets.items()])

        if valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class FormSetCreateView(FormSetMixin, ExtraContextMixin, edit.CreateView):
    template_name = 'generics/create_fieldsets.html'

    def get_fieldsets(self):
        fieldsets = {}

        for field in self.model._meta.many_to_many:

            target_model = field.related.parent_model

            # For m2m without a through model, use modelformset_factory.
            # For m2m with a thorough model, inlineformset_factory is
            # saves a bunch of work.
            # 
            # Determine which one to use by this HACKY method:
            # Check for underscores in through model name, 
            # since the auto-generated m2m tables have an underscore.

            has_through_model = field.rel.through._meta.object_name.find('_') == -1

            args = [self.request.POST, self.request.FILES] if self.request.method == 'POST' else []
            kwargs = {}

            factory_kwargs = self.factory_extra_args[field.name] if field.name in self.factory_extra_args else {}

            if has_through_model:
                fieldset_cls = inlineformset_factory(self.model, 
                    field.rel.through, extra=self.extra, **factory_kwargs)
            else:
                fieldset_cls = modelformset_factory(target_model, 
                    extra=self.extra, can_delete = self.can_delete, **factory_kwargs)

                kwargs['prefix'] = field.name
                kwargs['queryset'] = target_model.objects.none()

            fieldsets[field.name] = fieldset_cls(*args, **kwargs)

        return fieldsets


    def post(self, request, *args, **kwargs):
        self.object = None
        return super(FormSetCreateView, self).post(request, *args, **kwargs)


class FormSetUpdateView(FormSetMixin, ExtraContextMixin, edit.UpdateView):
    template_name = 'generics/update_fieldsets.html'

    def get_fieldsets(self):
        obj = self.get_object()

        fieldsets = {}

        for field in self.model._meta.many_to_many:

            target_model = field.related.parent_model

            # For m2m without a through model, use modelformset_factory.
            # For m2m with a thorough model, inlineformset_factory is
            # saves a bunch of work.
            # 
            # Determine which one to use by this HACKY method:
            # Check for underscores in through model name, 
            # since the auto-generated m2m tables have an underscore.

            has_through_model = field.rel.through._meta.object_name.find('_') == -1

            args = [self.request.POST, self.request.FILES] if self.request.method == 'POST' else []
            kwargs = {}

            factory_kwargs = self.factory_extra_args[field.name] if field.name in self.factory_extra_args else {}

            if has_through_model:
                fieldset_cls = inlineformset_factory(self.model, 
                    field.rel.through, extra=self.extra, **factory_kwargs)

                kwargs['instance'] = obj
            else:
                fieldset_cls = modelformset_factory(target_model, 
                    extra=self.extra, can_delete = self.can_delete, **factory_kwargs)

                kwargs['prefix'] = field.name
                kwargs['queryset'] = getattr(obj, field.name).all()

            fieldsets[field.name] = fieldset_cls(*args, **kwargs)

        return fieldsets


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(FormSetUpdateView, self).get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(FormSetUpdateView, self).post(request, *args, **kwargs)

