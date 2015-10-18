# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.utils.translation import ugettext_lazy as _

try:
    from django.apps import AppConfig
except ImportError:
    class AppConfig(object):
        pass


class BlogAppConfig(AppConfig):
    name = 'djangocms_blog'
    verbose_name = _('django CMS Blog')

    @staticmethod
    def setup():
        from cms.api import create_page, create_title
        from cms.exceptions import NoHomeFound
        from cms.models import Page
        from cms.utils import get_language_list
        from cms.utils.conf import get_templates
        from django.utils.translation import override

        from .cms_appconfig import BlogConfig
        from .settings import get_setting

        if get_setting('AUTO_SETUP'):
            configs = BlogConfig.objects.all()
            if not configs.exists():
                config = BlogConfig.objects.create(namespace='Blog')
                langs = get_language_list()
                blog = None
                for lang in langs:
                    with override(lang):
                        config.set_current_language(lang)
                        config.app_title = get_setting('AUTO_APP_TITLE')
                        config.save()
                        default_template = get_templates()[0][0]
                        try:
                            home = Page.objects.get_home()
                        except NoHomeFound:
                            home = None
                        if not home:
                            home = create_page(
                                get_setting('AUTO_HOME_TITLE'), language=lang,
                                template=default_template, in_navigation=True, published=True
                            )
                        elif lang not in home.get_languages():
                            create_title(
                                language=lang, title=get_setting('AUTO_HOME_TITLE'), page=home
                            )
                            home.publish(lang)
                        if not blog:
                            blog = create_page(
                                get_setting('AUTO_BLOG_TITLE'), language=lang, apphook='BlogApp',
                                apphook_namespace=config.namespace, parent=home,
                                template=default_template, in_navigation=True, published=True
                            )
                        else:
                            create_title(
                                language=lang, title=get_setting('AUTO_BLOG_TITLE'), page=blog
                            )
                            blog.publish(lang)
