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

Permalinks must be updated to avoid blog urlconf swallowing django CMS page patters.

To avoid this add the following settings to you project:

.. code-block:: python

    BLOG_AVAILABLE_PERMALINK_STYLES = (
        ('full_date', _('Full date')),
        ('short_date', _('Year /  Month')),
        ('category', _('Category')),
    )
    BLOG_PERMALINK_URLS = {
        'full_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'short_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'category': r'^(?P<category>\w[-\w]*)/(?P<slug>\w[-\w]*)/$',
    }

Notice that the last permalink type is no longer present.

Then, pick any of the three remaining permalink types in the layout section of the apphooks config
linked ot the home page (at http://yoursite.com/admin/djangocms_blog/blogconfig/).'
