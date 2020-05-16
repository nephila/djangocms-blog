.. _media:

##############################
Media plugins - Vlog / Podcast
##############################

Publising a vlog or a podcast require more introspection on the plugin contents
than is generally available to django CMS plugins.

djangocms-blog provides a mixin for plugin models and templatetags to
help when dealing with this use case.

For convenience, an additional ``media`` placeholder has been added to the
``Post`` model.

.. note:: djangocms-blog **only** provide a generic interface to introspect
          media plugins but it does not provide any plugin for any media
          platform as they would be very hard to maintain as the platforms
          changes. Examples provided here are working at the time of writing
          but they may require changes to work.


************
Base classes
************

.. autoclass:: djangocms_blog.media.base.MediaAttachmentPluginMixin
    :members:
    :private-members:


.. automodule:: djangocms_blog.templatetags.djangocms_blog
    :members:


******************************
How to build the media plugins
******************************

#. Create a plugin model
    Create a plugin model inheriting from ``CMSPlugin`` or a subclass of it
    and add :py:class:`djangocms_blog.media.base.MediaAttachmentPluginMixin`
    mixin.

#. Provide the media configuration
    Populate :py:attr:`djangocms_blog.media.base.MediaAttachmentPluginMixin._media_autoconfiguration`.

#. Implement required properties
    Provide an implementation for the following properties:

    * :py:attr:`djangocms_blog.media.base.MediaAttachmentPluginMixin.media_url`

#. Add any additional properties / method suitable for your case.
    See ``media_title`` field in the ``Vimeo`` model below.


Example
=======

Plugin model
------------

This is a basic example for a Vimeo plugin.

As covers cannot be calculated from the video id, we must download the related
json and extract information from there. This model use the ``'callable'``
parameter in :py:attr:`djangocms_blog.media.base.MediaAttachmentPluginMixin._media_autoconfiguration`

.. code-block:: python
   :name: my_app/models.py

    class Vimeo(MediaAttachmentPluginMixin, CMSPlugin):
        url = models.URLField('Video URL')

        _media_autoconfiguration = {
            'params': [
                re.compile('^https://vimeo.com/(?P<media_id>[-0-9]+)$'),
            ],
            'thumb_url': '%(thumb_url)s',
            'main_url': '%(main_url)s',
            'callable': 'vimeo_data',
        }

        def __str__(self):
            return self.url

        @property
        def media_id(self):
            try:
                return self.media_params['id']
            except KeyError:
                return None

        @property
        def media_title(self):
            try:
                return self.media_params['title']
            except KeyError:
                return None

        @property
        def media_url(self):
            return self.url

        def vimeo_data(self, media_id):
            response = requests.get(
                'https://vimeo.com/api/v2/video/%(media_id)s.json' % {'media_id': media_id, }
            )
            json = response.json()
            data = {}
            if json:
                data = json[0]
                data.update(
                    {
                        'main_url': data['thumbnail_large'],
                        'thumb_url': data['thumbnail_medium'],
                    }
                )
            return data


Plugin class
------------

Plugin class does not require any special code / configuration and can be
setup as usual.

.. code-block:: python
   :name: my_app/cms_plugins.py

    @plugin_pool.register_plugin
    class VimeoPlugin(CMSPluginBase):
        model = Vimeo
        module = 'Media'
        name = 'Vimeo'
        render_template = 'media_app/vimeo.html'



***************************************
How to display information in templates
***************************************

The actual implementation may vary a lot according to your design. To ease
retrieving the plugins, check :py:func:`djangocms_blog.templatetags.djangocms_blog.media_images`
:py:func:`djangocms_blog.templatetags.djangocms_blog.media_plugins` which abstract
away a lot of the django CMS logic to retrieve the plugins for a placeholder.

It's important to remember that at least in *some* templates, you must have the
``media`` placeholder rendered using ``{% render_placeholder post.media %}``
templatetag, otherwise you will not be able to add the plugins to the blog post.

Example
=======

Media plugin
------------

The media plugin requires the normal template to render the video according
to the plugin fields:

.. code-block:: html+django
   :name: media_app/vimeo.html

    {% if instance.media_id %}<iframe src="https://player.vimeo.com/video/{{ instance.media_id }}?badge=0&autopause=0&player_id=0&app_id=2221" width="1920" height="1080" frameborder="0" title="{{ instance.media_title }}" allow="autoplay; fullscreen" allowfullscreen></iframe>{% endif %}


Blog posts list
---------------

A basic implementation is retrieving the covers associated to each media content via
:py:func:`djangocms_blog.templatetags.djangocms_blog.media_images` and rendering each
with a ``<img>`` tag:

.. code-block:: html+django
   :name: templates/djangocms_blog/post_list.html

    ...
    {% media_images post as previews %}
    <div class="blog-visual">
      {% for preview in previews %}<img src="{{ preview }}" />{% endfor %}
    </div>
    ...

Blog posts detail
-----------------

A basic implementation is rendering the media plugins as you would do with normal plugins:

.. code-block:: html+django
   :name: templates/djangocms_blog/post_detail.html

    ...
    {% if not post.main_image_id %}
        <div class="blog-visual">{% render_placeholder post.media %}</div>
    {% else %}
    ...

***********************
djangocms-video support
***********************

``poster`` attribute from ``djangocms-video`` is also supported.

``poster`` is just a static fixed-size image you can set to a
``djangocms-video`` instance, but adding the plugin to the ``media``
placeholder allows to extract the image from the field and display along with
the generated previews by seamlessly using ``media_images``.

The rendering of the full content is of course fully supported.
