from django.db.models import SlugField

__all__ = ['AutoSlugField']


class AutoSlugField(SlugField):
    def __init__(self, *args, **kwargs):
        self.allow_unicode = kwargs.pop('allow_unicode', False)
        super(SlugField, self).__init__(*args, **kwargs)
