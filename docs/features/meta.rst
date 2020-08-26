.. _meta:

###############################
Setup social metatags rendering
###############################

djangocms-blog implements `django-meta <https://github.com/nephila/django-meta>`_ and it come ready to provide a
fairly complete social meta tags set.

Custom metatags are rendered on the blog post detail page only, while on the list page (which is a basically django CMS page)
you can use `djangocms-page-meta <https://github.com/nephila/djangocms-page-meta/>`_ to render meta tags based on the django CMS
page object.

In order to enable its rendering you must follow two steps:

* Enable ``django-meta`` settings in the project ``settings.py``

  .. code-block:: python

      META_SITE_PROTOCOL = 'https'  # set 'http' for non ssl enabled websites
      META_USE_SITES = True
      META_USE_OG_PROPERTIES=True
      META_USE_TWITTER_PROPERTIES=True
      META_USE_GOOGLEPLUS_PROPERTIES=True # django-meta 1.x+
      META_USE_SCHEMAORG_PROPERTIES=True  # django-meta 2.x+


* Include ``meta/meta.html`` in the ``head`` tag of the template used to render ``djangocms-blog``.

  a. The recommended way is to include in your project base templates:

     .. code-block:: html+django
         :name: base_a.html

         <html>
         <head>
            <title>{% block title %}{% page_attribute 'title' %}{% endblock title %}</title>
            {% include "meta/meta.html" %}
            ...

  b. alternatively djangocms-blog base template provide a ``meta`` block you can place in your templates to only include ``meta.html``
     for the blog posts:

     .. code-block:: html+django
         :name: base_b.html

         <html>
         <head>
            <title>{% block title %}{% page_attribute 'title' %}{% endblock title %}</title>
            {% block meta %}{% endblock meta %}
            ...

  c. If you are also using ``djangocms-page-meta`` use this base template to make the two packages interoperable:

     .. code-block:: html+django
         :name: base_c.html

         {% load page_meta_tags %}
         {% page_meta request.current_page as page_meta %}
         <html>
         <head>
            <title>{% block title %}{% page_attribute 'title' %}{% endblock title %}</title>
            {% block meta %}
            {% include 'djangocms_page_meta/meta.html' with meta=page_meta %}
            {% endblock meta %}
            ...

For complete social meta tags rendering, configure default properties (see ``BLOG_FB``, ``BLOG_TWITTER``, ``BLOG_GPLUS``/``BLOG_SCHEMAORG`` in :ref:`settings`) and apphook ones.
