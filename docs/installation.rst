.. _installation:

############
Installation
############

django CMS blog assumes a **completely setup and working django CMS project**.
See `django CMS installation docs <https://django-cms.readthedocs.io/en/latest/how_to/index.html#set-up>`_ for reference.

If you are not familiar with django CMS you are **strongly encouraged** to read django CMS documentation before installing django CMS blog, as setting it up and adding blog content require to use django CMS features which are not described in this documentation.

django CMS docs:

- `django CMS tutorial <http://docs.django-cms.org/en/latest/introduction/index.html>`_
- `django CMS user guide <http://docs.django-cms.org/en/latest/user/index.html>`_
- `django CMS videos <https://www.youtube.com/channel/UCafBqF_OeeGDgQVte5eCiJg>`_


**************************
django-app-enabler support
**************************

`django-app-enabler`_ is supported.

You can either

* Installation & configuration: ``python -mapp_enabler install djangocms-blog``
* Autoconfiguration: ``python -mapp_enabler enable djangocms_blog``

You can further customise the blog configuration, you can start by checking:

- :ref:`modify_templates`
- :ref:`haystack`
- :ref:`attach`
- :ref:`external_applications`

*********************
Installation steps
*********************

.. note:: The steps in this section are applied automatically by ``django-app-enabler``, if you use it.

* Install djangocms-blog:

  .. code-block:: python

      pip install djangocms-blog

* Add ``djangocms_blog`` and its dependencies to INSTALLED_APPS:

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


.. note:: The following are minimal defaults to get the blog running; they may not be
          suited for your deployment.

* Add the following settings to your project:

  .. code-block:: python

        THUMBNAIL_PROCESSORS = (
            'easy_thumbnails.processors.colorspace',
            'easy_thumbnails.processors.autocrop',
            'filer.thumbnail_processors.scale_and_crop_with_subject_location',
            'easy_thumbnails.processors.filters',
        )
        META_SITE_PROTOCOL = 'https'  # set 'http' for non ssl enabled websites
        META_USE_SITES = True

* For meta tags support enable the needed types::

        META_USE_OG_PROPERTIES=True
        META_USE_TWITTER_PROPERTIES=True
        META_USE_GOOGLEPLUS_PROPERTIES=True # django-meta 1.x+
        META_USE_SCHEMAORG_PROPERTIES=True  # django-meta 2.x+

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

* Apply the migrations:

  .. code-block:: bash

        python manage.py migrate

* Add the blog application (see :ref:`attach` below).

.. _modify_templates:

***********************
Modify templates
***********************

For standard djangocms-blog templates to work to must ensure a ``content`` block is available in the django CMS template
used by the page djangocms-blog is attached to.

For example, in case the page use the ``base.html`` template, you must ensure that something like the following is
in the template:

.. code-block:: html+django
    :name: base.html

    ...
    {% block content %}
        {% placeholder "page_content" %}
    {% endblock content %}
    ...

Alternative you can override then ``djangocms_blog/base.html`` and extend a different block


.. code-block:: html+django
    :name: djangocms_blog/base.html

    ...
    {% block my_block %}
    <div class="app app-blog">
        {% block content_blog %}{% endblock %}
    </div>
    {% endblock my_block %}
    ...

.. _haystack:

***********************
Enable haystack support
***********************

If you want to enable haystack support:

* install djangocms-blog with:

  .. code-block:: python

        pip install djangocms-blog[search]

* add ``aldryn_search`` to ``INSTALLED_APPS``
* configure haystack according to `aldryn-search docs <https://github.com/aldryn/aldryn-search#usage>`_
  and `haystack docs <http://django-haystack.readthedocs.io/en/stable/>`_.
* if not using ``aldryn_search``, you can define your own ``search_indexes.py`` by skipping ``aldryn_search`` installation and writing
  your index for blog posts by following haystack documentation.

.. _attach:

*************************
Attach the blog to a page
*************************

* To start your blog you need to use `AppHooks from django CMS <http://docs.django-cms.org/en/latest/how_to/apphooks.html>`_
  to add the blog to a django CMS page; this step is not required when using
  `Auto setup <https://github.com/nephila/djangocms-blog/blob/develop/docs/installation.rst#auto-setup>`_:

  * Create a new django CMS page
  * Go to **Advanced settings** and select Blog from the **Application** selector and
    create an **Application configuration**;
  * Eventually customise the Application instance name;
  * Publish the page
  * Restart the project instance to properly load blog urls.

  Check the :ref:`blog-home-page` section to attach the blog on the website home page.

.. warning:: After adding the apphook to the page you **cannot** change the **Instance Namespace**
             field for the defined **AppHokConfig**; if you want to change it, create a new one
             with the correct namespace, go in the CMS page **Advanced settings** and switch to the
             new **Application configuration**

* Add and edit blog by creating them in the admin or using the toolbar,
  and the use the `django CMS frontend editor`_.
  to edit the blog content:

  * Create a new blog entry in django admin backend or from the toolbar
  * Click on "view on site" button to view the post detail page
  * Edit the post via djangocms frontend by adding / editing plugins
  * Publish the blog post by flagging the "Publish" switch in the blog post
    admin

.. note:: by default djangocms-blog uses django CMS plugins for content, this means you will **not** have a text field
          in the blog post admin, but you will have to visit the frontend blog page (hit "Visit on site" button on
          the upper right corner) and add django CMS plugins on the frontend. Check the `tutorial`_ for
          more details.

.. _external_applications:

***********************************
Further configuration
***********************************

As django CMS heavily relies on external applications to provide its features, you may also want to check the documentation of external packages.


Please, refer to each application documentation on details.


* django-cms (framework and content plugins): http://django-cms.readthedocs.io/en
* django-filer (image handling): https://django-filer.readthedocs.io
* django-meta (meta tag handling): https://github.com/nephila/django-meta#installation
* django-parler (multi language support): https://django-parler.readthedocs.io/en/latest/quickstart.html#configuration
* aldryn-search (content search): https://github.com/aldryn/aldryn-search#usage>
* haystack (content search): http://django-haystack.readthedocs.io/en/stable/

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

.. _django cms frontend editor: http://docs.django-cms.org/en/latest/user/reference/page_admin.html
.. _tutorial: http://docs.django-cms.org/en/latest/user/tutorial/structure-content-modes.html
.. _django-app-enabler: https://github.com/nephila/django-app-enabler
