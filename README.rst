==============
djangocms-blog
==============


.. image:: https://img.shields.io/pypi/v/djangocms-blog.svg
        :target: https://pypi.python.org/pypi/djangocms-blog
        :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/nephila/djangocms-blog.svg
        :target: https://travis-ci.org/nephila/djangocms-blog
        :alt: Latest Travis CI build status

.. image:: https://img.shields.io/pypi/dm/djangocms-blog.svg
        :target: https://pypi.python.org/pypi/djangocms-blog
        :alt: Monthly downloads

.. image:: https://coveralls.io/repos/nephila/djangocms-blog/badge.png
        :target: https://coveralls.io/r/nephila/djangocms-blog
        :alt: Test coverage

.. image:: https://codeclimate.com/github/nephila/djangocms-blog/badges/gpa.svg
   :target: https://codeclimate.com/github/nephila/djangocms-blog
   :alt: Code Climate


A djangoCMS 3 blog application.

Supported Django versions:

* Django 1.6
* Django 1.7
* Django 1.8

Supported django CMS versions:

* django CMS 3.x


.. warning:: Version 0.6 changes the field of LatestPostsPlugin.tags field.
             A datamigration is in place to migrate the data, but check that
             works ok for your project before upgrading, as this might delete
             some relevant data.

.. warning:: Starting from version 0.5, this package does not declare dependency
             on South anymore; please install it separately if using this
             application on Django 1.6.


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

* If you are using Django 1.7+, be aware than ``filer`` < 0.9.10, ``cmsplugin_filer``
  and ``django-cms`` < 3.1 currently requires you to setup ``MIGRATION_MODULES`` in settings::

    MIGRATION_MODULES = {
       'cms': 'cms.migrations_django', # only for django CMS 3.0
       'menus': 'menus.migrations_django',  # only for django CMS 3.0
       'filer': 'filer.migrations_django',  # only for django filer 0.9.9 and below
       'cmsplugin_filer_image': 'cmsplugin_filer_image.migrations_django',
    }

  Please check
  `django CMS installation <http://django-cms.readthedocs.org/en/support-3.0.x/how_to/integrate.html#installing-and-configuring-django-cms-in-your-django-project>`_,
  `cmsplugin-filer README <https://github.com/stefanfoulis/cmsplugin-filer#installation>`_
  for detailed information.

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

* To start your blog you need to use `AppHooks from django CMS <http://django-cms.readthedocs.org/en/support-3.0.x/how_to/apphooks.html>`_
  to add the blog to a django CMS page:

  * Create a new django CMS page
  * Go to Advanced settings and select Blog from the Application selector;
  * Eventually customise the Application instance name;
  * Publish the page
  * Restart the project instance to properly load blog urls.

* Add and edit blog by creating them in the admin or using the toolbar,
  and the use the `django CMS frontend editor <http://django-cms.readthedocs.org/en/support-3.0.x/user/reference/page_admin.html#the-interface>`_
  to edit the blog content:

  * Create a new blog entry in django admin backend or from the toolbar
  * Click on "view on site" button to view the post detail page
  * Edit the post via djangocms frontend by adding / editing plugins
  * Publish the blog post by flagging the "Publish" switch in the blog post admin

Configurable permalinks
+++++++++++++++++++++++

Blog comes with four different styles of permalinks styles:

* Full date: ``YYYY/MM/DD/SLUG``
* Year /  Month: ``YYYY/MM/SLUG``
* Category: ``CATEGORY/SLUG``
* Just slug: ``SLUG``

As all the styles are loaded in the urlconf, the latter two does not allow to have CMS pages
beneath the page the blog is attached to. If you want to do this, you have to override the default
urlconfs by setting somethik like the following in the project settings::

    BLOG_PERMALINK_URLS = {
        'full_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'short_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'category': r'^post/(?P<category>\w[-\w]*)/(?P<slug>\w[-\w]*)/$',
        'slug': r'^post/(?P<slug>\w[-\w]*)/$',
    }

And change ``post/`` with the desired prefix.

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
* BLOG_USE_ABSTRACT: Use an abstract field for the post; if ``False`` no abstract field
  is available for every post; (default: True)
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


Known djangocms-blog websites
+++++++++++++++++++++++++++++

* http://nephila.co.uk/blog
* https://blog.ungleich.ch/
