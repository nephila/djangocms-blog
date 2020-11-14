from cms.utils.plugins import get_plugins
from django import template

register = template.Library()


@register.simple_tag(name="media_plugins", takes_context=True)
def media_plugins(context, post):
    """
    Extract :py:class:`djangocms_blog.media.base.MediaAttachmentPluginMixin`
    plugins from the ``media`` placeholder of the provided post.

    They can be rendered with ``render_plugin`` templatetag:

    .. code-block: python

        {% media_plugins post as media_plugins %}
        {% for plugin in media_plugins %}{% render_plugin plugin %}{% endfor %}

    :param context: template context
    :type context: dict
    :param post: post instance
    :type post: :py:class:`djangocms_blog.models.Post`
    :return: list of :py:class:`djangocms_blog.media.base.MediaAttachmentPluginMixin` plugins
    :rtype: List[djangocms_blog.media.base.MediaAttachmentPluginMixin]
    """
    request = context["request"]
    if post.media.get_plugins().exists():
        return get_plugins(request, post.media, None)
    return []


@register.simple_tag(name="media_images", takes_context=True)
def media_images(context, post, main=True):
    """
    Extract images of the given size from all the
    :py:class:`djangocms_blog.media.base.MediaAttachmentPluginMixin`
    plugins in the ``media`` placeholder of the provided post.

    Support ``djangocms-video`` ``poster`` field in case the plugin
    does not implement ``MediaAttachmentPluginMixin`` API.

    Usage:

    .. code-block: python

        {% media_images post False as thumbs %}
        {% for thumb in thumbs %}<img src="{{ thumb }}/>{% endfor %}

    .. code-block: python

        {% media_images post as main_images %}
        {% for image in main_images %}<img src="{{ image }}/>{% endfor %}

    :param context: template context
    :type context: dict
    :param post: post instance
    :type post: :py:class:`djangocms_blog.models.Post`
    :param main: retrieve main image or thumbnail
    :type main: bool
    :return: list of images urls
    :rtype: list
    """
    plugins = media_plugins(context, post)
    if main:
        image_method = "get_main_image"
    else:
        image_method = "get_thumb_image"
    images = []
    for plugin in plugins:
        try:
            images.append(getattr(plugin, image_method)())
        except Exception:
            try:
                image = plugin.poster
                if image:
                    images.append(image.url)
            except AttributeError:
                pass
    return images
