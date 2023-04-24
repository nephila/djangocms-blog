
.. _permalinks:

#######################
Configurable permalinks
#######################

Blog comes with four different styles of permalinks styles:

* Full date: ``YYYY/MM/DD/SLUG``
* Year /  Month: ``YYYY/MM/SLUG``
* Category: ``CATEGORY/SLUG``
* Just slug: ``SLUG``

As all the styles are loaded in the urlconf, the latter two does not allow
to have CMS pages beneath the page the blog is attached to. If you want to
do this, you have to override the default urlconfs by setting something
like the following in the project settings:

.. code-block:: python

    BLOG_PERMALINK_URLS = {
        "full_date": "<int:year>/<int:month>/<int:day>/<str:slug>/",
        "short_date": "<int:year>/<int:month>/<str:slug>/",
        "category": "<str:category>/<str:slug>/",
        "slug": "<str:slug>/",
    }

And change ``post/`` with the desired prefix.

.. warning:: Version 1.2 introduce a breaking change as it drops ``url`` function in favour of ``path``.
             If you have customized the urls as documented above you **must** update the custom urlconf to path-based
             patterns.
