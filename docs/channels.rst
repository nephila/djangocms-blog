.. _channels_features:

#################
Channels Features
#################

djangocms-blog implements some channels related features:

* desktop notifications
* liveblog

For how to setup channels in your project, please refer to `channels documentation`_.

.. _knocker:

*************
Notifications
*************

``djangocms-blog`` is integrated with `django-knocker`_
to provide real time desktop notifications.

See `django-knocker documentation`_ for how to configure
knocker.


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

To enabled liveblog features:

* Setup django channels according to `channels documentation`_

* Add ``djangocms_blog.liveblog`` application to ``INSTALLED_APPS``::

      INSTALLED_APPS = [
          ...
          'djangocms_blog.liveblog',
          ...
      ]

* If you overwrite the post detail template, setup the following javascript code in the custom
  template::

      {% add_data "js-script" "liveblog/js/reconnecting-websocket.min.js" %}
      {% add_data "js-script" "liveblog/js/liveblog.js" %}
      <script>
          var liveblog_apphook = '{{ post.app_config.namespace }}';
          var liveblog_language = '{{ post.get_current_language }}';
          var liveblog_post = '{{ post.slug }}';
      </script>

* It's advised to configure ``CMS_PLACEHOLDER_CONF`` to only allow ``Liveblog`` plugins in
  ``Liveblog`` placeholder, and remove them from other placeholders::

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

To customize the appearance of the plugin, just override the ``liveblog/plugins/liveblog.html``
template. Both the real time and non realtime version of the plugin will be rendered accordingly.

If you need something different, you can create your own plugin by creating your own plugin
inheriting from ``LiveblogInterface`` and calling the method ``self._post_save()`` in the
save method, after the model has been saved.

In ``models.py``:

.. code-block:: django

    class MyLiveblog(LiveblogInterface, CMSPlugin):
    """
    Basic liveblog plugin model
    """
    text = models.TextField(_('text'))

    def save(self, *args, **kwargs):
        super(MyLiveblog, self).save(*args, **kwargs)
        self._post_save()


The plugin class does not require any special inheritance; in ``cms_plugins.py``:

.. code-block:: django

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
