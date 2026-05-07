from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _
from djangocms_apphook_setup.base import AutoCMSAppMixin

from .cms_appconfig import BlogConfig
from .cms_menus import BlogCategoryMenu
from .compat import CMS_4_PLUS
from .settings import get_setting


@apphook_pool.register
class BlogApp(AutoCMSAppMixin, CMSConfigApp):
    name = _("Blog")
    _urls = [get_setting("URLCONF")]
    app_name = "djangocms_blog"
    app_config = BlogConfig
    _menus = [BlogCategoryMenu]
    auto_setup = {
        "enabled": get_setting("AUTO_SETUP"),
        "home title": get_setting("AUTO_HOME_TITLE"),
        "page title": get_setting("AUTO_BLOG_TITLE"),
        "namespace": get_setting("AUTO_NAMESPACE"),
        "config_fields": {},
        "config_translated_fields": {
            "app_title": get_setting("AUTO_APP_TITLE"),
            "object_name": get_setting("DEFAULT_OBJECT_NAME"),
        },
    }

    def get_urls(self, page=None, language=None, **kwargs):
        return [get_setting("URLCONF")]

    @property
    def urls(self):
        return self.get_urls()

    @property
    def menus(self):
        return self._menus

    # django CMS 3.x compatibility: the two classmethods below override
    # djangocms_apphook_setup's base versions which call page.publish() and
    # page.get_draft_object() — APIs removed in CMS 4.x.
    # When CMS 3.x support is dropped, remove the `if CMS_4_PLUS:` block and
    # make these the unconditional implementations (or delete entirely if
    # djangocms_apphook_setup is updated to support CMS 4.x natively).
    if CMS_4_PLUS:
        @classmethod
        def _create_page(cls, page, lang, auto_title, cms_app=None, parent=None, namespace=None, site=None, set_home=False):
            """CMS 4.x override: page.publish() and page.get_draft_object() no longer exist."""
            from cms.api import create_page, create_title
            from cms.utils.conf import get_templates

            default_template = get_templates()[0][0]
            if page is None:
                page = create_page(
                    auto_title,
                    language=lang,
                    parent=parent,
                    site=site,
                    template=default_template,
                    in_navigation=True,
                )
                page.application_urls = cms_app
                page.application_namespace = namespace
                page.save()
            elif lang not in page.get_languages():
                create_title(language=lang, title=auto_title, page=page)
            if set_home:
                page.set_as_homepage()
            return page

        @classmethod
        def _setup_pages(cls, config):
            """CMS 4.x override: Page.get_draft_object() no longer exists."""
            from cms.exceptions import NoHomeFound
            from cms.models import Page
            from cms.utils import get_language_list
            from django.contrib.sites.models import Site
            from django.utils.translation import override

            app_page = None
            site = Site.objects.get_current()
            auto_sites = cls.auto_setup.get("sites", True)
            if auto_sites is True or site.pk in auto_sites:
                if getattr(cls, "app_config", False):
                    configs = cls.app_config.objects.all()
                    if not configs.exists():
                        config = cls._create_config()
                    else:
                        config = configs.first()

                langs = get_language_list(site.pk)
                if not Page.objects.on_site(site.pk).filter(application_urls=cls.__name__).exists():
                    for lang in langs:
                        with override(lang):
                            if config:
                                if cls.auto_setup["config_translated_fields"]:
                                    cls._create_config_translation(config, lang)
                                namespace = config.namespace
                            elif cls.app_name:
                                namespace = cls.app_name
                            else:
                                namespace = None
                            try:
                                home = Page.objects.get_home(site.pk)
                            except NoHomeFound:
                                home = None
                            set_home = hasattr(Page, "set_as_homepage")
                            home = cls._create_page(
                                home, lang, cls.auto_setup["home title"], site=site, set_home=set_home
                            )
                            app_page = cls._create_page(
                                app_page, lang, cls.auto_setup["page title"], cls.__name__, home, namespace, site=site
                            )


BlogApp.setup()
