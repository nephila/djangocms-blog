
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
        'full_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'short_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'category': r'^post/(?P<category>\w[-\w]*)/(?P<slug>\w[-\w]*)/$',
        'slug': r'^post/(?P<slug>\w[-\w]*)/$',
    }

And change ``post/`` with the desired prefix.
