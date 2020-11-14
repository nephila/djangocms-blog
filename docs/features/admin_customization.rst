.. _admin_customization:

###################
Admin customization
###################

As any other django model admin, :py:class:`PostAdmin` can be customized by extending it adding a subclass in one of the
project's applications.

.. code-block:: python
   :name: project_app/admin.py

    admin.site.unregister(Post)
    @admin.register(Post)
    class CustomPostAdmin(PostAdmin):
        ...
        you_attributes_and_methods


*************************
Customizing the fieldsets
*************************

Due to the logic in :py:meth:`djangocms_blog.admin.PostAdmin.get_fieldsets` method, it's advised to customize the
fieldsets by overriding two private attributes :py:attr:`djangocms_blog.admin.PostAdmin._fieldsets` and
:py:attr:`djangocms_blog.admin.PostAdmin._fieldset_extra_fields_position`.

_fieldsets
=================

``_fieldsets`` attribute follow the standard `Django Admin fieldset`_ structure. This is the primary source for customization.

You can freely rearrange and remove fields from this structure as you would to in a normal ``fieldsets`` attribute; the only
caveat is that you must ensure consistency extra fields position set by ``_fieldset_extra_fields_position``.


_fieldset_extra_fields_position
===============================

As some fields are managed by settings and apphook config, they are added to the final ``fieldsets`` by ``PostAdmin.get_fieldsets``;
you can customize their position (or hide them) by overriding ``_fieldset_extra_fields_position`` attribute.

The attribute is a dictionary containing the fields name as key, and by providing their position in the fieldsets as tuple.

Use a 2-item tuple if the field must be appended at the row level (e.g.: ``(None, {"fields": ["field_a", "field_b"]})``) or
a 3-item tuple if the field must be appended in a subgroup (e.g.: ``(None, {"fields": ["field_a", ["field_b"[]})``.

Example
===============================

.. code-block:: python
   :name: my_app/admin.py

    admin.site.unregister(Post)
    @admin.register(Post)
    class CustomPostAdmin(PostAdmin):
        ...
        _fieldsets = [
            (None, {"fields": ["title", "subtitle", "slug", "publish", "categories"]}),
            (
                _("Info"),
                {
                    "fields": [["tags"], ["date_published", "date_published_end", "date_featured"], "app_config", "enable_comments"],
                    "classes": ("collapse",),
                },
            ),
            (
                _("Images"),
                {"fields": [["main_image", "main_image_thumbnail", "main_image_full"]], "classes": ("collapse",)},
            ),
            (_("SEO"), {"fields": [["meta_description", "meta_title", "meta_keywords"]], "classes": ("collapse",)}),
        ]
        _fieldset_extra_fields_position = {
            "abstract": [0, 1],
            "post_text": [0, 1],
            "sites": [1, 1, 0],
            "author": [1, 1],
            "enable_liveblog": None,
            "related": [1, 1, 0],
        }

This example will result in:

* ``"enable_liveblog"``: hidden even if enabled in settings
* ``"sites"``: added in the same subgroup as ``"tags"``
* ``"author"``: appended after the ``"enable_comments"`` field
* ``"app_config"`` field moved to ``"Info"`` fieldset


.. _admin_filter_function:

Filter function
===============

You can add / remove / filter fields at runtime by defining a method on you custom admin and proving its name in :ref:`BLOG_ADMIN_POST_FIELDSET_FILTER <ADMIN_POST_FIELDSET_FILTER>`.

Method must take the following arguments:

* ``fsets``: current fieldsets dictionary
* ``request``: current admin request
* ``obj`` (default: ``None``): current post object (if available)

and it must return the modified fieldsets dictionary.

Function example:

.. code-block:: python

    def fieldset_filter_function(fsets, request, obj=None):
        if request.user.groups.filter(name='Editor').exists():
            fsets[1][1]['fields'][0].append('author')  # adding 'author' field if user is Editor
        return fsets


.. _django admin fieldset: https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
