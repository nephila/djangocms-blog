# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.cms_plugins import TextPlugin

from djangocms_blog.settings import get_setting

from .models import Liveblog


class LiveblogPlugin(TextPlugin):
    module = get_setting('PLUGIN_MODULE_NAME')
    name = _('Liveblog item')
    model = Liveblog
    fields = ('title', 'publish', 'body', 'post_date')
    render_template = 'liveblog/plugins/liveblog.html'

    def save_model(self, request, obj, form, change):
        super(LiveblogPlugin, self).save_model(request, obj, form, change)
        if obj.publish:
            obj.send(request)

    def render(self, context, instance, placeholder):
        context = super(LiveblogPlugin, self).render(context, instance, placeholder)
        instance.content = context['body']
        context['instance'] = instance
        return context


plugin_pool.register_plugin(LiveblogPlugin)
