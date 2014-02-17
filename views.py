from django.views.generic import edit
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


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


class CreateView(ExtraContextMixin, edit.CreateView):
    """CreateView that offers extra_context and a default template."""
    template_name = 'generics/create.html'


class UpdateView(ExtraContextMixin, edit.UpdateView):
    """UpdateView that offers extra_context and a default template."""
    template_name = 'generics/update.html'


class DeleteView(ExtraContextMixin, edit.DeleteView):
    """DeleteView that offers extra_context and a default template."""
    template_name = 'generics/delete.html'


class UserViewMixin(object):
    """
    This mixin alters a generic create view that has a "created_by" field by
    automatically setting the user field to the current user.
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
