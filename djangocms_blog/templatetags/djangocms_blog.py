# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.utils.plugins import get_plugins
from django import template

register = template.Library()


@register.simple_tag(name='media_images', takes_context=True)
def media_images(context, post):
    request = context['request']
    if post.media.get_plugins().exists():
        plugins = get_plugins(request, post.media, None)
        return [
            plugin.get_thumb_image() for plugin in plugins if hasattr(plugin, 'get_thumb_image')
        ]
    return []
