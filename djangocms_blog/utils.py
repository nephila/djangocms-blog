import django
from django.db import models
from parler.models import TranslatedFieldsModelBase, TranslatedFieldsModel, \
    _lazy_verbose_name
import sys


def create_translations_model(shared_model, related_name, meta, **fields):
    """
    Dynamically create the translations model.
    Create the translations model for the shared model 'model'.

    :param related_name: The related name for the reverse FK from the translations model.
    :param meta: A (optional) dictionary of attributes for the translations model's inner Meta class.
    :param fields: A dictionary of fields to put on the translations model.

    Two fields are enforced on the translations model:

        language_code: A 15 char, db indexed field.
        master: A ForeignKey back to the shared model.

    Those two fields are unique together.
    """
    if not meta:
        meta = {}

    if shared_model._meta.abstract:
        # This can't be done, because `master = ForeignKey(shared_model)` would fail.
        raise TypeError("Can't create TranslatedFieldsModel for abstract class {0}".format(shared_model.__name__))

    # Define inner Meta class
    meta['app_label'] = shared_model._meta.app_label
    meta['db_tablespace'] = shared_model._meta.db_tablespace
    meta['managed'] = shared_model._meta.managed
    meta['unique_together'] = list(meta.get('unique_together', []))
    meta.setdefault('db_table', '{0}_translation'.format(shared_model._meta.db_table))
    meta.setdefault('verbose_name', _lazy_verbose_name(shared_model))

    # Avoid creating permissions for the translated model, these are not used at all.
    # This also avoids creating lengthy permission names above 50 chars.
    if django.VERSION >= (1,7):
        meta.setdefault('default_permissions', ())

    # Define attributes for translation table
    name = str('{0}Translation'.format(shared_model.__name__))  # makes it bytes, for type()

    attrs = {}
    attrs.update(fields)
    attrs['Meta'] = type(str('Meta'), (object,), meta)
    attrs['__module__'] = shared_model.__module__
    attrs['objects'] = models.Manager()
    attrs['master'] = models.ForeignKey(shared_model, related_name=related_name, editable=False, null=True)

    # Create and return the new model
    translations_model = TranslatedFieldsModelBase(name, (TranslatedFieldsModel,), attrs)

    # Register it as a global in the shared model's module.
    # This is needed so that Translation model instances, and objects which refer to them, can be properly pickled and unpickled.
    # The Django session and caching frameworks, in particular, depend on this behaviour.
    mod = sys.modules[shared_model.__module__]
    setattr(mod, name, translations_model)

    return translations_model


class TranslatedFields(object):
    """
    Wrapper class to define translated fields on a model.

    The field name becomes the related name of the :class:`TranslatedFieldsModel` subclass.

    Example:

    .. code-block:: python

        from django.db import models
        from parler.models import TranslatableModel, TranslatedFields

        class MyModel(TranslatableModel):
            translations = TranslatedFields(
                title = models.CharField("Title", max_length=200)
            )

    When the class is initialized, the attribute will point
    to a :class:`~django.db.models.fields.related.ForeignRelatedObjectsDescriptor` object.
    Hence, accessing ``MyModel.translations.related.model`` returns the original model
    via the :class:`django.db.models.related.RelatedObject` class.

    ..
       To fetch the attribute, you can also query the Parler metadata:
       MyModel._parler_meta.get_model_by_related_name('translations')
    """
    def __init__(self, meta=None, **fields):
        self.fields = fields
        self.meta = meta
        self.name = None

    def contribute_to_class(self, cls, name):
        # Called from django.db.models.base.ModelBase.__new__
        self.name = name
        create_translations_model(cls, name, self.meta, **self.fields)