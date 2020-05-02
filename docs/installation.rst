.. _installation:

############
Installation
############

django CMS blog assumes a **completely setup and working django CMS project**.
See `django CMS installation docs <https://django-cms.readthedocs.io/en/latest/how_to/index.html#set-up>`_ for reference.

Install djangocms-blog:

.. code-block:: python

    pip install djangocms-blog

Add ``djangocms_blog`` and its dependencies to INSTALLED_APPS:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'filer',
        'easy_thumbnails',
        'aldryn_apphooks_config',
        'parler',
        'taggit',
        'taggit_autosuggest',
        'meta',
        'sortedm2m',
        'djangocms_blog',
        ...
    ]


Then apply migrations:

.. code-block:: python

    python manage.py migrate

If you want to enable haystack support, in addition to the above:

* install djangocms-blog with:

.. code-block:: python

    pip install djangocms-blog[search]

* add ``aldryn_search`` to ``INSTALLED_APPS``
* configure haystack according to `aldryn-search docs <https://github.com/aldryn/aldryn-search#usage>`_
  and `haystack docs <http://django-haystack.readthedocs.io/en/stable/>`_.

To enable taggit filtering support in the admin install djangocms-blog with:

.. code-block:: python

    pip install djangocms-blog[taggit]

*********************
Minimal configuration
*********************

The following are minimal defaults to get the blog running; they may not be
suited for your deployment.

* Add the following settings to your project:

.. code-block:: python

    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    )
    META_SITE_PROTOCOL = 'http'
    META_USE_SITES = True

* For meta tags support enable the needed types::

    META_USE_OG_PROPERTIES=True
    META_USE_TWITTER_PROPERTIES=True
    META_USE_GOOGLEPLUS_PROPERTIES=True

* Configure parler according to your languages:

.. code-block:: python

    PARLER_LANGUAGES = {
        1: (
            {'code': 'en',},
            {'code': 'it',},
            {'code': 'fr',},
        ),
        'default': {
            'fallbacks': ['en', 'it', 'fr'],
        }
    }

.. note:: Since parler 1.6 this can be skipped if the language configuration is the same as ``CMS_LANGUAGES``.

* Add the following to your ``urls.py``:

.. code-block:: python

    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),

* To start your blog you need to use `AppHooks from django CMS <http://docs.django-cms.org/en/latest/how_to/apphooks.html>`_
  to add the blog to a django CMS page; this step is not required when using
  `Auto setup <https://github.com/nephila/djangocms-blog/blob/develop/docs/installation.rst#auto-setup>`_:

  * Create a new django CMS page
  * Go to **Advanced settings** and select Blog from the **Application** selector and
    create an **Application configuration**;
  * Eventually customise the Application instance name;
  * Publish the page
  * Restart the project instance to properly load blog urls.

.. warning:: After adding the apphook to the page you **cannot** change the **Instance Namespace**
             field for the defined **AppHokConfig**; if you want to change it, create a new one
             with the correct namespace, go in the CMS page **Advanced settings** and switch to the
             new **Application configuration**

* Add and edit blog by creating them in the admin or using the toolbar,
  and the use the `django CMS frontend editor <http://docs.django-cms.org/en/latest/user/reference/page_admin.html>`_
  to edit the blog content:

  * Create a new blog entry in django admin backend or from the toolbar
  * Click on "view on site" button to view the post detail page
  * Edit the post via djangocms frontend by adding / editing plugins
  * Publish the blog post by flagging the "Publish" switch in the blog post
    admin

.. _external_applications:

***********************************
External applications configuration
***********************************

Dependency applications may need configuration to work properly.

Please, refer to each application documentation on details.

* django-cms: http://django-cms.readthedocs.io/en/release-3.4.x/how_to/install.html
* django-filer: https://django-filer.readthedocs.io
* django-meta: https://github.com/nephila/django-meta#installation
* django-meta-mixin: https://github.com/nephila/django-meta-mixin#installation
* django-parler: https://django-parler.readthedocs.io/en/latest/quickstart.html#configuration
* django-taggit-autosuggest: https://bitbucket.org/fabian/django-taggit-autosuggest
* aldryn-search: https://github.com/aldryn/aldryn-search#usage>
* haystack: http://django-haystack.readthedocs.io/en/stable/

.. _auto_setup:

**********
Auto setup
**********

``djangocms_blog`` can install and configue itself if it does not find any
attached instance of itself.
This feature is enable by default and will create:

* a ``BlogConfig`` with default values
* a ``Blog`` CMS page and will attach ``djangocms_blog`` instance to it
* a **home page** if no home is found.

All the items will be created in every language configured for the website
and the pages will be published. If not using **aldryn-apphook-reload** or
**django CMS 3.2** auto-reload middleware you are required to reload the
project instance after this.
This will only work for the current website as detected by
``Site.objects.get_current()``.


The auto setup is execute once for each server start but it will skip any
action if a ``BlogConfig`` instance is found.
