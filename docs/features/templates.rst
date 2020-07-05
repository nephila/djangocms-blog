
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

.. _templates_set:

*************
Templates set
*************

You can provide a different set of templates for the whole ``djangocms-blog`` application by configuring
the ``Blog configs`` accordingly.

This would require you to customize **all** the templates shipped in ``djangocms_blog/templates/djangocms_blog``; the easiest
way would be to copy the **content** of ``djangocms_blog/templates/djangocms_blog`` into another folder in the ``templates``
folder in our project
(e.g., something like ``cp -a djangocms_blog/templates/djangocms_blog/* /path/my/project/templates/my_blog``).

To use the new templates set, go to the ``Blog configs`` admin
(something like ``http://localhost:8000/en/admin/djangocms_blog/blogconfig/1/change``) and enter a directory name in the
**Template prefix** field in the **Apphook configuration** admin (in the *Layout* section): it will be the
root of your custom templates set; following the example above, you should enter ``my_blog`` as directory name.

For more instruction regarding template override, please read Django documentation: `Overriding templates`_ (for your version of Django).

.. _plugin_templates:

****************
Plugin Templates
****************

You can have different layouts for each plugin (i.e.: ``Latest Blog Articles``, ``Author Blog Articles List`` etc), by
having multiple templates for each plugin.
Default plugin templates are located in the ``plugins`` folder of the folder specified by the **Template prefix**;
by default they are located in ``templates/djangocms_blog``.

By defining the setting ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` you can allow multiple sets of
plugin templates allowing for different views per plugin instance. You could, for example,
have a plugin displaying latest posts as a list, a table or in masonry style.

New templates have the same names as the standard templates in the ``plugins`` folder
(e.g: ``latest_entries.html``, ``authors.html``, ``tags.html``, ``categories.html``, ``archive.html``).

When using this feature you **must** provide **all** the templates for the available plugins.

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


.. _overriding templates: https://docs.djangoproject.com/en/dev/howto/overriding-templates/#overriding-templates
