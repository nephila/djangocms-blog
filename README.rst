==============
djangocms-blog
==============


.. image:: https://pypip.in/v/djangocms-blog/badge.png
        :target: https://pypi.python.org/pypi/djangocms-blog
        :alt: Latest PyPI version
    
.. image:: https://travis-ci.org/nephila/djangocms-blog.png?branch=master
        :target: https://travis-ci.org/nephila/djangocms-blog
        :alt: Latest Travis CI build status

.. image:: https://pypip.in/d/djangocms-blog/badge.png
        :target: https://pypi.python.org/pypi/djangocms-blog
        :alt: Monthly downloads

.. image:: https://coveralls.io/repos/nephila/djangocms-blog/badge.png?branch=master
        :target: https://coveralls.io/r/nephila/djangocms-blog?branch=master
        :alt: Test coverage



A djangoCMS 3 blog application.

Still experimental and untested. You are welcome if you want to try it; if
you encounter any issue, please open an issue.

Supported Django versions:

* Django 1.5
* Django 1.6
* Django 1.7

Supported django CMS versions:

* django CMS 3.0

.. warning:: Starting from version 0.3 the length of the meta_description and
             meta_title fields has been changed according to the most common
             defaults for search engines. Existing data will not be affected,
             but widgets that enforce the length for new data is now being used.

.. warning:: Starting from 0.3 BlogLatestEntriesPlugin and BlogAuthorPostsPlugin
             the plugin API has changed: ``BlogLatestEntriesPlugin.get_posts``,
             ``BlogAuthorPostsPlugin.get_authors`` requires the ``request``
             argument. Templates has been changed to use a context variable
             instead. Please update your plugin templates accordingly.

.. warning:: To ease migration to version 0.3, djangocms-blog depends on south
             even on Django 1.7; while this is unnecessary for Dajngo 1.7, it
             makes transition to version 0.3 painless. Hard dependency will be
             removed in 0.5.


Quickstart
----------

Install djangocms-blog::

    pip install djangocms-blog

Add ``djangocms_blog`` and its dependencies to INSTALLED_APPS::

    INSTALLED_APPS = [
        ...
        'filer',
        'easy_thumbnails',
        'cmsplugin_filer_image',
        'parler',
        'taggit',
        'taggit_autosuggest',
        'django_select2',
        'meta',
        'meta_mixin',
        'admin_enhancer',
        'djangocms_blog',
        ...
    ]

Then sync and migrate::

    $ python manage.py syncdb
    $ python manage.py migrate

External applications configuration
+++++++++++++++++++++++++++++++++++

Dependency applications may need configuration to work properly.

Please, refer to each application documentation on details.

* django-filer: http://django-filer.readthedocs.org
* django-meta: https://github.com/nephila/django-meta#installation
* django-parler: http://django-parler.readthedocs.org/en/latest/quickstart.html#configuration
* django-taggit-autosuggest: https://bitbucket.org/fabian/django-taggit-autosuggest

Quick hint
++++++++++

The following are minimal defaults to get the blog running; they may not be
suited for your deployment.

* Add the following settings to your project::    

    SOUTH_MIGRATION_MODULES = {
        'easy_thumbnails': 'easy_thumbnails.south_migrations',
        'taggit': 'taggit.south_migrations',
    }
    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    )
    META_SITE_PROTOCOL = 'http'
    META_USE_SITES = True

* Configure parler according to your languages::

    PARLER_LANGUAGES = {
        1: (
            {'code': 'en',},
            {'code': 'it',},
            {'code': 'fr',},
        ),
    }

* Add the following to your ``urls.py``::

    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),

* To start your blog create a new page from the CMS and hook it to the blog application:
 
  * Create a new django CMS page
  * Go to Advanced settings and sele select Blog from the Application selector;
  * Eventually customise the Application instance name;
  * Restart the project instance to properly load blog urls.


Templates
+++++++++

To ease the template customisations a ``djangocms_blog/base.html`` template is used by all the blog templates;
the templates itself extends a ``base.html`` template; content is pulled in the ``content`` block.
If you need to define a different base template, or if your base template does not defines a ``content`` block,
copy in your template directory ``djangocms_blog/base.html`` and customise it according to your
needs; the other application templates will use the newly created template and will ignore the bundled one.

Features
--------

* Placeholder content editing
* Frontend editing using django CMS 3.0 frontend editor
* Multilingual support using django-parler
* Support for Twitter cards, Open Graph and Google+ snippets meta tags
* Optional support for simpler TextField-based content editing
* Multisite support (posts can be visible in one or more Django sites on the same project)

Import from Wordpress
+++++++++++++++++++++

If you want to import content from existing wordpress blog, check
https://pypi.python.org/pypi/the-real-django-wordpress and
this gist https://gist.github.com/yakky/11336204 as a base.


Settings
--------
* BLOG_ENABLE_COMMENTS: Whether to enable comments by default on posts;
  while ``djangocms_blog`` does not ship any comment system, this flag can be used
  to control the chosen comments framework; (default: True)
* BLOG_USE_PLACEHOLDER: Post content is managed via placeholder; if ``False`` a
  simple HTMLField is used; (default: True)
* BLOG_IMAGE_THUMBNAIL_SIZE: Size of the main image when shown on the post lists;
  it's a dictionary with ``size``, ``crop`` and ``upscale`` keys;
  (default: ``{'size': '120x120', 'crop': True,'upscale': False}``)
* BLOG_IMAGE_FULL_SIZE: Size of the main image when shown on the post detail;
  it's a dictionary with ``size``, ``crop`` and ``upscale`` keys;
  (default: ``{'size': '640x120', 'crop': True,'upscale': False}``)
* BLOG_PAGINATION: Number of post per page; (default: 10)
* BLOG_LATEST_POSTS: Default number of post in the **Latest post** plugin; (default: 5)
* BLOG_POSTS_LIST_TRUNCWORDS_COUNT: Default number of words shown for abstract in the post list; (default: 100)
* BLOG_MULTISITE: Add support for multisite setup
* BLOG_AUTHOR_DEFAULT: Use a default if not specified; if set to ``True`` the
  current user is set as the default author, if set to ``False`` no default
  author is set, if set to a string the user with the provided username is
  used; (default: True)

Social media tags settings
++++++++++++++++++++++++++
* BLOG_TYPE: Generic type for the post object; (default: Article)
* BLOG_FB_TYPE: Open Graph type for the post object; (default: Article)
* BLOG_FB_APPID: Facebook Application ID
* BLOG_FB_PROFILE_ID: Facebook profile ID of the post author
* BLOG_FB_PUBLISHER: Facebook URL of the blog publisher
* BLOG_FB_AUTHOR_URL: Facebook profile URL of the post author
* BLOG_FB_AUTHOR: Facebook profile URL of the post author
* BLOG_TWITTER_TYPE: Twitter Card type for the post object; (default: Summary)
* BLOG_TWITTER_SITE: Twitter account of the site
* BLOG_TWITTER_AUTHOR: Twitter account of the post author
* BLOG_GPLUS_TYPE: Google+ Snippet type for the post object; (default: Blog)
* BLOG_GPLUS_AUTHOR: Google+ account of the post author

.. image:: https://d2weczhvl823v0.cloudfront.net/nephila/djangocms-blog/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

