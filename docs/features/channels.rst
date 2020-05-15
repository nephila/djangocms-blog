.. _channels_features:

##########################################
Channels: Desktop notifications - Liveblog
##########################################

djangocms-blog implements some channels related features:

* desktop notifications
* liveblog

For detailed information on channels setup, please refer to `channels documentation`_.

.. warning:: channels support works only on Django 2.2 and up

.. _knocker:

*************
Notifications
*************

``djangocms-blog`` integrates `django-knocker`_ to provide real time desktop notifications.

To enable notifications:

* Install **django-knocker** and **channels<2.0**

* Add ``channels`` and ``knocker`` application to ``INSTALLED_APPS`` together with channels:

    .. code-block:: python

          INSTALLED_APPS = [
              ...
              'channels',
              'knocker',
              ...
          ]

* Load the ``knocker`` routing into channels configuration:

    .. code-block:: python

        ASGI_APPLICATION = 'myproject.routing.application'
        CHANNEL_LAYERS={
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
                },
            },
        }

* Add to ``myproject.routing.application`` the knocker routes:

    .. code-block:: python

        from channels.auth import AuthMiddlewareStack
        from channels.routing import ProtocolTypeRouter, URLRouter
        from django.urls import path
        from knocker.routing import channel_routing as knocker_routing

        application = ProtocolTypeRouter({
            'websocket': AuthMiddlewareStack(
                URLRouter([
                    path('knocker/', knocker_routing),
                ])
            ),
        })


* Load ``{% static "js/knocker.js" %}`` and ``{% static "js/reconnecting-websocket.min.js" %}`` into
  the templates

* Add the following code:

    .. code-block:: html+django

        <script type="text/javascript">
          var knocker_language = '{{ LANGUAGE_CODE }}';
          var knocker_url = '/notifications';  // Set this to the actual URL
        </script>

  The value of ``knocker_url`` must match the path configured in ``myproject.routing.channel_routing.py``.

* Enable notifications for each Apphook config level by checking the
  **Send notifications on post publish** and **Send notifications on post update**
  flags in blog configuration model.


.. _liveblog:

********
Liveblog
********

Liveblog feature allows to display any content on a single post in realtime.

This is implemented by creating a group for each liveblogging enabled post and assigning
the clients to each group whenever they visit a liveblog post.

Each liveblogged text is a specialized plugin (see `extend_liveblog`_ for information on how to
customize the liveblog plugin).


Enabling liveblog
=================

To enable liveblog features:

* Add ``djangocms_blog.liveblog`` application to ``INSTALLED_APPS`` together with channels:

    .. code-block:: python

          INSTALLED_APPS = [
              ...
              'channels',
              'djangocms_blog.liveblog',
              ...
          ]

* It's advised to configure ``CMS_PLACEHOLDER_CONF`` to only allow ``Liveblog`` plugins in
  ``Liveblog`` placeholder, and remove them from other placeholders:

    .. code-block:: python

          CMS_PLACEHOLDER_CONF = {
              None: {
                  'excluded_plugins': ['LiveblogPlugin'],
              }
              ...
              'liveblog': {
                   'plugins': ['LiveblogPlugin'],
              }
              ...
          }

* Add channels routing configuration:

    .. code-block:: python

        ASGI_APPLICATION = 'myproject.routing.application'
        CHANNEL_LAYERS={
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
                },
            },
        }

.. note:: Check `channels documentation`_ for more detailed information on ``CHANNEL_LAYERS`` setup.

* Add to ``myproject.routing.channel_routing.py`` the knocker routes:

    .. code-block:: python

        from channels.auth import AuthMiddlewareStack
        from channels.routing import ProtocolTypeRouter, URLRouter
        from django.urls import path

        from djangocms_blog.liveblog.routing import channel_routing as djangocms_blog_routing

        application = ProtocolTypeRouter({
            'websocket': AuthMiddlewareStack(
                URLRouter([
                    path('liveblog/', djangocms_blog_routing),
                ])
            ),
        })

* If you overwrite the post detail template, add the following code where you want to show
  the liveblog content:

    .. code-block:: html+django

          {% if view.liveblog_enabled %}
              {% include "liveblog/includes/post_detail.html" %}
          {% endif %}

Liveblob and notifications can be activated at the same time by configuring each.


Using liveblog
==============

To use liveblog:

* Tick the ``enable liveblog`` flag in the ``Info`` fieldset;
* Open the blog post detail page;
* Optionally add static content to the ``post content`` placeholder; the default template will
  show static content on top of liveblog content; you can override the template for different
  rendering;
* Add plugins to the ``Liveblog`` placeholder;
* Tick the ``publish`` flag on each ``Liveblog`` plugin to send it to clients in realtime.


.. _extend_liveblog:

Extending liveblog plugin
=========================

Liveblog support ships with a default liveblog plugin that provides a title, a body and
a filer image.

To customize the appearance of the plugin override the ``liveblog/plugins/liveblog.html``
template. Both the real time and non realtime version of the plugin will be rendered accordingly.

If you need something different, you can create your own plugin
inheriting from ``LiveblogInterface`` and calling the method ``self._post_save()`` in the
save method, after the model has been saved.

In ``models.py``:

.. code-block:: python

    class MyLiveblog(LiveblogInterface, CMSPlugin):
    """
    Basic liveblog plugin model
    """
    text = models.TextField(_('text'))

    def save(self, *args, **kwargs):
        super(MyLiveblog, self).save(*args, **kwargs)
        self._post_save()


The plugin class does not require any special inheritance; in ``cms_plugins.py``:

.. code-block:: python

    class MyLiveblogPlugin(CMSPluginBase):
        name = _('Liveblog item')
        model = MyLiveblog
    plugin_pool.register_plugin(MyLiveblogPlugin)

While not required, for consistency between between realtime and non realtime rendering, use the
``publish`` field inherited from ``LiveblogInterface`` to hide the plugin content when the plugin
is not published.


.. _channels documentation: http://channels.readthedocs.io/en/latest/index.html
.. _django-knocker documentation: http://django-knocker.readthedocs.io/en/latest/index.html
.. _django-knocker: https://github.com/nephila/django-knocker
