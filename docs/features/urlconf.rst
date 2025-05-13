
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
