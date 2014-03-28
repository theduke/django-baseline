from __future__ import unicode_literals

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CrispyFormMixin(object):
    """
    A mixin that adds a Crispy forms FormHelper object to a form.
    """

    SUBMIT_LABEL = 'Submit'
    HTTP_METHOD = 'post'

    def __init__(self, *args, **kwargs):
        super(CrispyFormMixin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.add_input(Submit('submit', self.SUBMIT_LABEL))
        self.helper.form_method =  self.HTTP_METHOD


class CrispyForm(CrispyFormMixin, forms.Form):
    """
    Convenience base class for regular forms which 
    will be rendered with crispy.
    """

    pass


class CrispyModelForm(CrispyFormMixin, forms.ModelForm):
    """
    Convenience base class for ModelForms which 
    will be rendered with crispy.
    """

    pass


class CrispyFormSetHelper(FormHelper):
    """
    A custom FormHelper with form tag disabled.
    Used for inline forms.
    """

    def __init__(self, *args, **kwargs):
        super(CrispyFormSetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False


class CrispyInlineParentForm(ModelForm):
    """
    Convenience ModelForm base class which uses a Crispy FormHelper
    with disabled form tag. Used for inline formsets in views.py.
    """

    def __init__(self, *args, **kwargs):
        super(InlineParentForm, self).__init__(*args, **kwargs)
        # Set to false because form set is used.
        # See http://django-crispy-forms.readthedocs.org/en/d-0/tags.html#rendering-several-forms-with-helpers.
        self.helper = CrispyFormSetHelper()
