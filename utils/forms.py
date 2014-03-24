from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CrispyFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CrispyFormSetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False


class CrispyForm(ModelForm):

    SUBMIT_LABEL = 'Submit'
    HTTP_METHOD = 'post'

    def __init__(self, *args, **kwargs):
        super(CrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.add_input(Submit('submit', self.SUBMIT_LABEL))
        self.helper.form_method =  self.HTTP_METHOD


class InlineParentForm(ModelForm):


    def __init__(self, *args, **kwargs):
        super(InlineParentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # Set to false because form set is used.
        # See http://django-crispy-forms.readthedocs.org/en/d-0/tags.html#rendering-several-forms-with-helpers.
        self.helper.form_tag = False
