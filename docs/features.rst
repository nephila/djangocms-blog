.. _features:

========
Features
========

.. _blog-home-page:

*******************************
Attaching blog to the home page
*******************************

If you want to attach the blog to the home page you have to adapt settings a bit otherwise the
"Just slug" permalink will swallow any CMS page you create.

To avoid this add the following settings to you project::

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
linked ot the home page (see http://yoursite.com/admin/djangocms_blog/blogconfig/).'

.. _blog-custom-urlconf:

************************
Provide a custom URLConf
************************

It's possible to completely customize the urlconf by setting ``BLOG_URLCONF`` to the dotted path of
the new urlconf.

Example::

    BLOG_URLCONF = 'my_project.blog_urls.py'

The custom urlconf can be created by copying the existing urlconf in `djangocms_blog/urls.py`,
saving it to a new file `my_project.blog_urls.py` and editing it according to the custom needs.


.. _multisite:

*********
Multisite
*********

django CMS blog provides full support for multisite setups.

Basic multisite
===============

To enabled basic multisite add ``BLOG_MULTISITE = True`` to the project settings.

Each blog post can be assigned to none, one or more sites: if no site is selected, then
it's visible on all sites. All users with permission on the blog can manage all the blog
posts, whichever the sites are.

Multisite permissions
=====================

Multisite permissions allow to restrict users to only manage the blog posts for the
sites they are enabled to

To implement the multisite permissions API, you must add a ``get_sites`` method on
the user model which returns a queryset of sites the user is allowed to add posts to.

Example::

    class CustomUser(AbstractUser):
        sites = models.ManyToManyField('sites.Site')

        def get_sites(self):
            return self.sites

.. _cms-wizard:

**********************
django CMS 3.2+ Wizard
**********************

django CMS 3.2+ provides a content creation wizard that allows to quickly created supported
content types, such as blog posts.

For each configured Apphook, a content type is added to the wizard.

Some issues with multiple registrations raising django CMS ``AlreadyRegisteredException``
hae been reported; to handle these cases gracefully, the exception is swallowed
when Django ``DEBUG == True`` avoiding breaking production websites. In these cases they
wizard may not show up, but the rest will work as intended.

.. _permalinks:

***********************
Configurable permalinks
***********************

Blog comes with four different styles of permalinks styles:

* Full date: ``YYYY/MM/DD/SLUG``
* Year /  Month: ``YYYY/MM/SLUG``
* Category: ``CATEGORY/SLUG``
* Just slug: ``SLUG``

As all the styles are loaded in the urlconf, the latter two does not allow
to have CMS pages beneath the page the blog is attached to. If you want to
do this, you have to override the default urlconfs by setting something
like the following in the project settings::

    BLOG_PERMALINK_URLS = {
        'full_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'short_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'category': r'^post/(?P<category>\w[-\w]*)/(?P<slug>\w[-\w]*)/$',
        'slug': r'^post/(?P<slug>\w[-\w]*)/$',
    }

And change ``post/`` with the desired prefix.

.. _menu:

****
Menu
****

``djangocms_blog`` provides support for django CMS menu framework.

By default all the categories and posts are added to the menu, in a hierarchical structure.

It is possibile to configure per Apphook, whether the menu includes post and categories
(the default), only categories, only posts or no item.

If "post and categories" or "only categories" are set, all the posts not associated with a
category are not added to the menu.

.. _templates:

*********
Templates
*********

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

Example:::

    BLOG_PLUGIN_TEMPLATE_FOLDERS = (
        ('plugins', _('Default template')),    # reads from templates/djangocms_blog/plugins/
        ('timeline', _('Vertical timeline')),  # reads from templates/djangocms_blog/vertical/
        ('masonry', _('Masonry style')),       # reads from templates/djangocms_blog/masonry/
    )

Once defined, the plugin admin interface will allow content managers to select which template the plugin will use.

.. _sitemap:

*******
Sitemap
*******

``djangocms_blog`` provides a sitemap for improved SEO indexing.
Sitemap returns all the published posts in all the languages each post is available.

The changefreq and priority is configurable per-apphook (see ``BLOG_SITEMAP_*`` in
`Global settings <settings>`_).

To add the blog Sitemap, add the following code to the project ``urls.py``::


    from cms.sitemaps import CMSSitemap
    from djangocms_blog.sitemaps import BlogSitemap


    urlpatterns = patterns(
        '',
        ...
        url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
            {'sitemaps': {
                'cmspages': CMSSitemap, 'blog': BlogSitemap,
            }
        }),
    )


*************
Social shares
*************

``djangocms_blog`` integrates well with options for social shares. One of the many options available is Shariff_ which was developed by a popular German computer magazine.

.. _Shariff: https://github.com/heiseonline/shariff

To allow readers to share articles on Facebook, Twitter, LinkedIn or just mail them, simply add share buttons to your ``post_detail.html`` template just before ``</article>``.

If you decide to use Shariff this just requires a simple ``<div>`` to be added (see documentation of shariff). Here is a simple template tag that loads all required conifigurations and javascript files. The ``<div>`` becomes ``{% shariff %}``: ::

    from django.conf import settings
    from django import template

    register = template.Library()

    @register.inclusion_tag('djangocms_blog/shariff.html', takes_context=True)
    def shariff(context, title=None, services=None, orientation=None):
        context['orientation'] = orientation if orientation else 'horizontal'
        context['services'] = escape(services if services else
                                    settings.SHARIFF['services'])  # MUST be configured in settings.py
        if title:
            context['short_message'] = settings.SHARIFF.get('prefix', '') + title +\
                          settings.SHARIFF.get('postfix', '')
        if 'mail-url' in settings.SHARIFF:
            context['mail_url'] = settings.SHARIFF['mail-url']
        return(context)

And in ``templates/djangocms_blog/shariff.html`` you simply need ::

    {% load static sekizai_tags %}
    {% addtoblock 'js' %}<script src="{% static 'js/shariff.min.js' %}"></script>{% endaddtoblock %}
    {% addtoblock 'css' %}<link href="{% static 'css/shariff.min.css' %}" rel="stylesheet">{% endaddtoblock %}
    <div class="shariff" data-services="{{services}}" data-orientation="{{orientation}}"{% if mail_url %} data-mail-url="{{mail_url}}"{% endif %}{% if short_message %} data-title="{{short_message}}"{% endif %}></div>

The shariff files ``js/shariff.min.js`` and ``css/shariff.min.css`` will need to be added to your static files. Also, a little configuration in ``settings.py`` is needed, e.g.,

::

    SHARIFF = {
        'services': '["twitter", "facebook", "googleplus", "linkedin", "xing", "mail"]',
        'mail-url': 'mailto:',                  # optional
        'prefix':   'Have you seen this: "',	# optional
        'postfix':  '"',                        # optional
    }
