
.. _blog-custom-urlconf:

################
Customizing URLs
################

************************
Provide a custom URLConf
************************

It's possible to completely customize the urlconf by setting ``BLOG_URLCONF`` to the dotted path of
the new urlconf.

Example:

.. code-block:: python

    BLOG_URLCONF = 'my_project.blog_urls'

The custom urlconf can be created by copying the existing urlconf in ``djangocms_blog/urls.py``,
saving it to a new file ``my_project.blog_urls.py`` and editing it according to the custom needs.

The default URLConf ``djangocms_blog/urls.py`` is based on post lists that can be filtered by
authors, categories, tags. Clicking an a post gives the post details.

.. _blog-apphook-urlconf:

**************************************
Allow to configure URLConf per apphook
**************************************

For some projects it makes sense to have different apphooks with different URLConf. Say, you have a
classic blog that reports current events. The classical blog list ordered by publication date
with newest posts up in the list. Another set of posts discusses key topics in depth. They do not
change significantly over time and should be ordered by topic rather than by publication date.
For this content hub an URLConf with a list of categories might be more appropriate.


Example:

.. code-block:: python

    BLOG_URLCONF = (
        ("djangocms_blog.urls", _("Blog: Blog list at root page")),
        ("djangocms_blog.urls_hub", _("Content hub: Category list at root page")),
    )

If ``BLOG_URLCONF`` is a list (or tuple) of 2-tuples a drop down box will appear in the
apphook configuration offering the options.
