from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag
from cms.utils.plugins import get_plugins
from cms.utils.urlutils import admin_reverse
from django import template

from djangocms_blog.models import PostContent

register = template.Library()


@register.simple_tag(name="media_plugins", takes_context=True)
def media_plugins(context, post_content):
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
    if post_content and post_content.media and post_content.media.get_plugins().exists():
        return get_plugins(context["request"], post_content.media, None)
    return []


@register.simple_tag(name="media_images", takes_context=True)
def media_images(context, post_content, main=True):
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
    plugins = media_plugins(context, post_content)
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


class GetAbsoluteUrl(AsTag):
    """Classy tag that returns the url for editing PageContent in the admin."""
    name = "absolute_url"
    post_content_type = None

    options = Options(
        Argument('post_content'),
        Argument("language", required=False, default=None),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def get_value(self, context, post_content, language):
        if not post_content:
            return ""

        toolbar = getattr(context["request"], "toolbar", None)
        if toolbar:
            if toolbar.edit_mode_active:
                return self.endpoint_url("cms_placeholder_render_object_edit", post_content)
            if toolbar.preview_mode_active:
                return self.endpoint_url("cms_placeholder_render_object_preview", post_content)
        return post_content.get_absolute_url(language)

    @staticmethod
    def endpoint_url(admin, obj):
        if GetAbsoluteUrl.post_content_type is None:
            # Use class as cache
            from django.contrib.contenttypes.models import ContentType

            GetAbsoluteUrl.post_content_type = ContentType.objects.get_for_model(PostContent).pk
        return admin_reverse(admin, args=[GetAbsoluteUrl.post_content_type, obj.pk])


register.tag(GetAbsoluteUrl.name, GetAbsoluteUrl)
