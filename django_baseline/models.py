from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


def get_object_or_none(qs, *args, **kwargs):
    """
    Try to retrieve a model, and return None if 
    it is not found. 
    Useful if you do not want to bother with the try/except block.
    """

    try:
        return qs.get(*args, **kwargs)
    except models.ObjectDoesNotExist:
        return None


class ContentTypeInheritanceBase(models.Model):
    """
    This models allows to easily create a model hierarchy with nested models.
    The lowest model in the hierarchy (the lowest child) can always be
    retrieved with get_child().
    """

    content_type = models.ForeignKey(ContentType, editable=False, null=True)

    @classmethod
    def get_content_type(cls):
        '''
        Get the content type of the class, useful for queries.
        '''
        return ContentType.objects.get_for_model(cls)

    def save(self):
        if (not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.save_base()

    def get_child(self):
        content_type = self.content_type
        model = content_type.model_class()
        if(model == ContentTypeInheritanceBase or model == self.__class__):
            return self

        return model.objects.get(id=self.id)

    class Meta:
        abstract = True


class TimeStampedModelMixin(object):
    """
    A model mixin for created_at and modified_at fields.
    """

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Modified at"), auto_now=True)
