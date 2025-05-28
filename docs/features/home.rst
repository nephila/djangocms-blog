.. _blog-home-page:

===============================
Attaching blog to the home page
===============================

*********************************
Add blog apphook to the home page
*********************************

* Go to the django CMS page admin: http://localhost:8000/admin/cms/page
* Edit the home page
* Go to **Advanced settings** and select Blog from the **Application** selector and create an **Application configuration**;
* Eventually customise the Application instance name;
* Publish the page
* Restart the project instance to properly load blog urls.

*******************
Amend configuration
*******************

Permalinks must be updated to avoid blog urlconf swallowing django CMS page patterns.

To avoid this add the following settings to your project:

.. code-block:: python

    BLOG_AVAILABLE_PERMALINK_STYLES = (
        ('full_date', _('Full date')),
        ('short_date', _('Year /  Month')),
        ('category', _('Category')),
    )
    BLOG_PERMALINK_URLS = {
        "full_date": "<int:year>/<int:month>/<int:day>/<str:slug>/",
        "short_date": "<int:year>/<int:month>/<str:slug>/",
        "category": "<str:category>/<str:slug>/",
    }

Notice that the last permalink type is no longer present.

Then, pick any of the three remaining permalink types in the layout section of the apphooks config
linked to the home page (at http://yoursite.com/admin/djangocms_blog/blogconfig/).'

.. warning:: Version 1.2 introduce a breaking change as it drops ``url`` function in favour of ``path``.
             If you have customized the urls as documented above you **must** update the custom urlconf to path-based
             patterns.
