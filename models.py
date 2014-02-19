from django.db import models
from django.contrib.contenttypes.models import ContentType


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
