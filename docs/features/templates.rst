
.. _templates:

#########
Templates
#########

To ease the template customisations a ``djangocms_blog/base.html`` template is
used by all the blog templates; the templates itself extends a ``base.html``
template; content is pulled in the ``content`` block.
If you need to define a different base template, or if your base template does
not defines a ``content`` block, copy in your template directory
``djangocms_blog/base.html`` and customise it according to your needs; the
other application templates will use the newly created base template and
will ignore the bundled one.

*************
Templates set
*************

By using **Apphook configuration** you can define a different templates set.
To use this feature provide a directory name in **Template prefix** field in
the **Apphook configuration** admin (in *Layout* section): it will be the
root of your custom templates set.

****************
Plugin Templates
****************

Plugin templates live in the ``plugins`` folder of the folder specified by the **Template prefix**,
or by default ``djangocms_blog``.

By defining the setting ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` you can allow multiple sets of
plugin templates allowing for different views per plugin instance. You could, for example,
have a plugin displaying latest posts as a list, a table or in masonry style.

To use this feature define ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` as a list of available templates.
Each item of this list itself is a list of the form ``('[folder_name]', '[verbose name]')``.

Example:

.. code-block:: python

    BLOG_PLUGIN_TEMPLATE_FOLDERS = (
        ('plugins', _('Default template')),    # reads from templates/djangocms_blog/plugins/
        ('timeline', _('Vertical timeline')),  # reads from templates/djangocms_blog/vertical/
        ('masonry', _('Masonry style')),       # reads from templates/djangocms_blog/masonry/
    )

Once defined, the plugin admin interface will allow content managers to select which template the plugin will use.
