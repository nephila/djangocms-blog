.. _installation:

############
Installation
############

Install djangocms-blog::

    pip install djangocms-blog

Add ``djangocms_blog`` and its dependencies to INSTALLED_APPS::

    INSTALLED_APPS = [
        ...
        'filer',
        'easy_thumbnails',
        'aldryn_apphooks_config',
        'cmsplugin_filer_image',
        'parler',
        'taggit',
        'taggit_autosuggest',
        'meta',
        'djangocms_blog',
        ...
    ]


Then migrate::

    $ python manage.py migrate

*********************
Minimal configuration
*********************

The following are minimal defaults to get the blog running; they may not be
suited for your deployment.

* Add the following settings to your project::

    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    )
    META_SITE_PROTOCOL = 'http'
    META_USE_SITES = True

* Add the following to your ``urls.py``::

    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),

* To start your blog you need to use `AppHooks from django CMS <http://docs.django-cms.org/en/latest/how_to/apphooks.html>`_
  to add the blog to a django CMS page; this step is not required when using
  `Auto setup <auto_setup>`_:

  * Create a new django CMS page
  * Go to **Advanced settings** and select Blog from the **Application** selector and
    create an **Application configuration**;
  * Eventually customise the Application instance name;
  * Publish the page
  * Restart the project instance to properly load blog urls.

.. warning:: After adding the apphook to the page you **cannot** change the **Instance Namspace**
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

* django-filer: https://django-filer.readthedocs.io
* django-meta: https://github.com/nephila/django-meta#installation
* django-meta-mixin: https://github.com/nephila/django-meta-mixin#installation
* django-parler: https://django-parler.readthedocs.io/en/latest/quickstart.html#configuration
* django-taggit-autosuggest: https://bitbucket.org/fabian/django-taggit-autosuggest


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
