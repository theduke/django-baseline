from __future__ import unicode_literals

import json

from django.shortcuts import render, render_to_response
from django.views.generic import edit
from django.views.generic import detail
from django.views import generic
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.messages.views import SuccessMessageMixin


from .forms import CrispyFormSetHelper

#######################
# Generic view MIXINS #
#######################

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
    property extra_context for easily passing additional context vars.
    """

    extra_context = {}


    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        # Add model verbose name to the context if needed in template.
        context['model_name'] = self.model._meta.verbose_name.capitalize()
        context.update(self.extra_context)
        return context


class SaveHookMixin(object):
    """
    A generic edit view mixin that provides pre_save and 
    post_save hooks.
    """

    def pre_save(self, object):
        """
        Hook for altering object before save.
        """

        pass


    def post_save(self, object):
        """
        Hook for altering object after save.
        """

        pass


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.pre_save(self.object)
        self.object.save()
        form.save_m2m()
        self.post_save(self.object)

        return HttpResponseRedirect(self.get_success_url())


class UserViewMixin(object):
    """
    IMPORTANT: REQUIRES SaveHookMixin!

    This mixin alters a generic CREATE view that has a "created_by" field by
    automatically setting the user field to the current user when the form is submitted.
    The field name of the field to populate is specified by the user_field
    property and defaults to created_by.
    """

    user_field = ['created_by']


    def __init__(self, *args, **kwargs):
        super(UserViewMixin, self).__init__(*args, **kwargs)
        # Ensure that user_field is a list.
        if type(self.user_field) == str:
            self.user_field = [self.user_field]


    def get_initial(self):
        """
        Supply user object as initial data for the specified user_field(s).
        """

        data = super(UserViewMixin, self).get_initial()
        for k in self.user_field:
            data[k] = self.request.user

        return data


    def pre_save(self, instance):
        """
        Use SaveHookMixin pre_save to set the user.
        """

        for field in self.user_field:
            setattr(instance, field, self.request.user)

#############################
# Generic view base classes #
#############################


class ListView(ExtraContextMixin, generic.ListView):
    template_name = "generics/list.html"


class DetailView(detail.DetailView):
    """
    DetailView which tries to show all the fields of a model.
    """

    template_name = "generics/detail.html"
    fields = None

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        #fields = self.fields or self.model._meta.get_all_field_names()
        #field_data = {name:getattr(self.object, name) for name in fields}

        #context['fields'] = field_data

        return context


class CreateView(SuccessMessageMixin, ExtraContextMixin, SaveHookMixin, edit.CreateView):
    """
    CreateView that offers extra_context and a default template.
    """

    template_name = 'generics/create.html'


class UpdateView(SuccessMessageMixin, ExtraContextMixin, SaveHookMixin, edit.UpdateView):
    """
    UpdateView that offers extra_context and a default template.
    """

    template_name = 'generics/update.html'


class DeleteView(SuccessMessageMixin, ExtraContextMixin, edit.DeleteView):
    """
    DeleteView that offers extra_context and a default template.
    """

    template_name = 'generics/delete.html'


class FormSetMixin(object):
    """
    A ModelForm mixin that makes creating views with inline 
    formsets really easy.
    Used by FormSetCreateView and FormSetUpdateView.
    """

    # The form class used for the inline items.
    inline_form_class = forms.ModelForm

    fields = None
    excluded_fields = ['created_at', 'created_by']

    # m2m fields that should be displayed with the default widget, 
    # instead of inline.
    forced_regular_fields = []

    extra = 1
    can_delete = True

    # Extra arguments for the formset factory for a field.
    factory_extra_args = {}

    # Whether the fieldset and the individual items should be  expanded.
    fieldsets_expanded = True
    fieldset_items_expanded = True


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
        context['fieldsets'] = self.get_fieldsets().items()
        context['helper'] = self.get_fieldset_crispy_helper()
        context['fieldsets_expanded'] = self.fieldsets_expanded
        context['fieldset_items_expanded'] = self.fieldset_items_expanded

        return context


    def pre_save(self, instance):
        """
        Hook for editing the instance.
        """

        pass


    def post_save(self, instance):
        for name, formset in self.formsets.items():
            instances = formset.save()
            for model in instances:
                getattr(instance, name).add(model)

        instance.save()


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


class FormSetCreateView(SuccessMessageMixin, ExtraContextMixin, FormSetMixin, SaveHookMixin, edit.CreateView):
    """
    CreateView for a model with inline forms of another model.
    """

    template_name = 'generics/create_fieldsets.html'
    extra = 3
    can_delete = False


    def get_fieldsets(self):
        fieldsets = {}

        for field in self.model._meta.many_to_many:

            target_model = field.related.parent_model

            # For m2m without a through model, use modelformset_factory.
            # For m2m with a thorough model, inlineformset_factory
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
                fieldset_cls = inlineformset_factory(self.model, field.rel.through,
                    form=self.inline_form_class, extra=self.extra, **factory_kwargs)
            else:
                fieldset_cls = modelformset_factory(target_model,  form=self.inline_form_class,
                    extra=self.extra, can_delete = self.can_delete, **factory_kwargs)

                kwargs['prefix'] = field.name
                kwargs['queryset'] = target_model.objects.none()

            fieldsets[field.name] = fieldset_cls(*args, **kwargs)

        return fieldsets


    def post(self, request, *args, **kwargs):
        self.object = None
        return super(FormSetCreateView, self).post(request, *args, **kwargs)


class FormSetUpdateView(SuccessMessageMixin, ExtraContextMixin, FormSetMixin, SaveHookMixin, edit.UpdateView):
    """
    UpdateView for a model with inline forms of another model.
    """

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
                fieldset_cls = inlineformset_factory(self.model, field.rel.through,
                    form=self.inline_form_class, extra=self.extra, **factory_kwargs)

                kwargs['instance'] = obj
            else:
                fieldset_cls = modelformset_factory(target_model,  form=self.inline_form_class,
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
