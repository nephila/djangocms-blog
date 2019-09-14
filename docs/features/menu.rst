
.. _menu:

####
Menu
####

``djangocms_blog`` provides support for django CMS menu framework.

By default all the categories and posts are added to the menu, in a hierarchical structure.

It is possibile to configure per Apphook, whether the menu includes post and categories
(the default), only categories, only posts or no item.

If "post and categories" or "only categories" are set, all the posts not associated with a
category are not added to the menu.

.. _sitemap:

#######
Sitemap
#######

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
