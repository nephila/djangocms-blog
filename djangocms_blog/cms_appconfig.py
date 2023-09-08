from cms.apphook_pool import apphook_pool
from django import forms
from django.db import models
from django.urls import Resolver404, resolve
from django.utils.translation import get_language_from_request, gettext_lazy as _, override
from filer.models import ThumbnailOption
from parler.models import TranslatableModel, TranslatedFields

from .settings import MENU_TYPE_COMPLETE, get_setting

config_defaults = {
    "default_image_full": None,
    "default_image_thumbnail": None,
    "url_patterns": get_setting("AVAILABLE_PERMALINK_STYLES")[0][0],
    "use_placeholder": get_setting("USE_PLACEHOLDER"),
    "use_abstract": get_setting("USE_ABSTRACT"),
    "use_related": int(get_setting("USE_RELATED")),
    "urlconf": get_setting("URLCONF") if isinstance(get_setting("URLCONF"), str) else get_setting("URLCONF")[0][0],
    "set_author": get_setting("AUTHOR_DEFAULT"),
    "paginate_by": get_setting("PAGINATION"),
    "template_prefix": "",
    "menu_structure": MENU_TYPE_COMPLETE,
    "menu_empty_categories": get_setting("MENU_EMPTY_CATEGORIES"),
    "sitemap_changefreq": get_setting("SITEMAP_CHANGEFREQ_DEFAULT"),
    "sitemap_priority": get_setting("SITEMAP_PRIORITY_DEFAULT"),
    "object_type": get_setting("TYPE"),
    "og_type": get_setting("FB_TYPE"),
    "og_app_id": get_setting("FB_PROFILE_ID"),
    "og_profile_id": get_setting("FB_PROFILE_ID"),
    "og_publisher": get_setting("FB_PUBLISHER"),
    "og_author_url": get_setting("FB_AUTHOR_URL"),
    "og_author": get_setting("FB_AUTHOR"),
    "twitter_type": get_setting("TWITTER_TYPE"),
    "twitter_site": get_setting("TWITTER_SITE"),
    "twitter_author": get_setting("TWITTER_AUTHOR"),
    "gplus_type": get_setting("SCHEMAORG_TYPE"),
    "gplus_author": get_setting("SCHEMAORG_AUTHOR"),
    "send_knock_create": False,
    "send_knock_update": False,
}


class BlogConfig(TranslatableModel):
    class Meta:
        verbose_name = _("blog config")
        verbose_name_plural = _("blog configs")

    type = models.CharField(
        _("Type"),
        max_length=100,
    )
    namespace = models.CharField(
        _("Instance namespace"),
        default=None,
        max_length=100,
        unique=True,
    )
    translations = TranslatedFields(
        app_title=models.CharField(_("application title"), max_length=200, default=get_setting("AUTO_APP_TITLE")),
        object_name=models.CharField(_("object name"), max_length=200, default=get_setting("DEFAULT_OBJECT_NAME")),
    )

    #: Default size of full images
    default_image_full = models.ForeignKey(
        ThumbnailOption,
        related_name="default_images_full",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Default size of full images"),
        help_text=_("If left empty the image size will have to be set for every newly created post."),
    )
    #: Default size of thumbnail images
    default_image_thumbnail = models.ForeignKey(
        ThumbnailOption,
        related_name="default_images_thumbnail",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Default size of thumbnail images"),
        help_text=_("If left empty the thumbnail image size will have to be set for every newly created post."),
    )
    #: Structure of permalinks (get_absolute_url); see :ref:`AVAILABLE_PERMALINK_STYLES <AVAILABLE_PERMALINK_STYLES>`
    url_patterns = models.CharField(
        max_length=12,
        verbose_name=_("Permalink structure"),
        blank=True,
        default=config_defaults["url_patterns"],
        choices=get_setting("AVAILABLE_PERMALINK_STYLES"),
    )
    #: Use placeholder and plugins for article body (default: :ref:`USE_PLACEHOLDER <USE_PLACEHOLDER>`)
    use_placeholder = models.BooleanField(
        verbose_name=_("Use placeholder and plugins for article body"),
        default=config_defaults["use_placeholder"],
    )
    #: Use abstract field (default: :ref:`USE_ABSTRACT <USE_ABSTRACT>`)
    use_abstract = models.BooleanField(verbose_name=_("Use abstract field"), default=config_defaults["use_abstract"])
    #: Enable related posts (default: :ref:`USE_RELATED <USE_RELATED>`)
    use_related = models.SmallIntegerField(
        verbose_name=_("Enable related posts"),
        default=config_defaults["use_related"],
        choices=(
            (0, _("No")),
            (1, _("Yes, from this blog config")),
            (2, _("Yes, from this site")),
        ),
    )
    #: Adjust urlconf (default: :ref:`USE_RELATED <USE_RELATED>`)
    urlconf = models.CharField(
        max_length=200,
        verbose_name=_("URL config"),
        default=config_defaults["urlconf"],
        choices=(
            [(get_setting("URLCONF"), "---")] if isinstance(get_setting("URLCONF"), str) else get_setting("URLCONF")
        ),
    )
    #: Set author by default (default: :ref:`AUTHOR_DEFAULT <AUTHOR_DEFAULT>`)
    set_author = models.BooleanField(
        verbose_name=_("Set author by default"),
        default=config_defaults["set_author"],
    )
    #: When paginating list views, how many articles per page? (default: :ref:`PAGINATION <PAGINATION>`)
    paginate_by = models.SmallIntegerField(
        verbose_name=_("Paginate size"),
        null=True,
        default=config_defaults["paginate_by"],
        help_text=_("When paginating list views, how many articles per page?"),
    )
    #: Alternative directory to load the blog templates from (default: "")
    template_prefix = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name=_("Template prefix"),
        help_text=_("Alternative directory to load the blog templates from"),
    )
    #: Menu structure (default: ``MENU_TYPE_COMPLETE``, see :ref:`MENU_TYPES <MENU_TYPES>`)
    menu_structure = models.CharField(
        max_length=200,
        choices=get_setting("MENU_TYPES"),
        default=MENU_TYPE_COMPLETE,
        verbose_name=_("Menu structure"),
        help_text=_("Structure of the django CMS menu"),
    )
    #: Show empty categories in menu (default: :ref:`MENU_EMPTY_CATEGORIES <MENU_EMPTY_CATEGORIES>`)
    menu_empty_categories = models.BooleanField(
        verbose_name=_("Show empty categories in menu"),
        default=get_setting("MENU_EMPTY_CATEGORIES"),
        help_text=_("Show categories with no post attached in the menu"),
    )
    #: Sitemap changefreq (default: :ref:`SITEMAP_CHANGEFREQ_DEFAULT <SITEMAP_CHANGEFREQ_DEFAULT>`,
    #: see: :ref:`SITEMAP_CHANGEFREQ <SITEMAP_CHANGEFREQ>`)
    sitemap_changefreq = models.CharField(
        max_length=12,
        choices=get_setting("SITEMAP_CHANGEFREQ"),
        default=get_setting("SITEMAP_CHANGEFREQ_DEFAULT"),
        verbose_name=_("Sitemap changefreq"),
        help_text=_("Changefreq attribute for sitemap items"),
    )
    #: Sitemap priority (default: :ref:`SITEMAP_PRIORITY_DEFAULT <SITEMAP_PRIORITY_DEFAULT>`)
    sitemap_priority = models.DecimalField(
        decimal_places=3,
        max_digits=5,
        default=get_setting("SITEMAP_PRIORITY_DEFAULT"),
        verbose_name=_("Sitemap priority"),
        help_text=_("Priority attribute for sitemap items"),
    )
    #: Object type (default: :ref:`TYPE <TYPE>`, see :ref:`TYPES <TYPES>`)
    object_type = models.CharField(
        max_length=200,
        blank=True,
        choices=get_setting("TYPES"),
        default=get_setting("TYPE"),
        verbose_name=_("Object type"),
    )
    #: Facebook type (default: :ref:`FB_TYPE <FB_TYPE>`, see :ref:`FB_TYPES <FB_TYPES>`)
    og_type = models.CharField(
        max_length=200,
        verbose_name=_("Facebook type"),
        blank=True,
        choices=get_setting("FB_TYPES"),
        default=get_setting("FB_TYPE"),
    )
    #: Facebook application ID (default: :ref:`FB_PROFILE_ID <FB_PROFILE_ID>`)
    og_app_id = models.CharField(
        max_length=200, verbose_name=_("Facebook application ID"), blank=True, default=get_setting("FB_PROFILE_ID")
    )
    #: Facebook profile ID (default: :ref:`FB_PROFILE_ID <FB_PROFILE_ID>`)
    og_profile_id = models.CharField(
        max_length=200, verbose_name=_("Facebook profile ID"), blank=True, default=get_setting("FB_PROFILE_ID")
    )
    #: Facebook page URL (default: :ref:`FB_PUBLISHER <FB_PUBLISHER>`)
    og_publisher = models.CharField(
        max_length=200, verbose_name=_("Facebook page URL"), blank=True, default=get_setting("FB_PUBLISHER")
    )
    #: Facebook author URL (default: :ref:`FB_AUTHOR_URL <FB_AUTHOR_URL>`)
    og_author_url = models.CharField(
        max_length=200, verbose_name=_("Facebook author URL"), blank=True, default=get_setting("FB_AUTHOR_URL")
    )
    #: Facebook author (default: :ref:`FB_AUTHOR <FB_AUTHOR>`)
    og_author = models.CharField(
        max_length=200, verbose_name=_("Facebook author"), blank=True, default=get_setting("FB_AUTHOR")
    )
    #: Twitter type field (default: :ref:`TWITTER_TYPE <TWITTER_TYPE>`)
    twitter_type = models.CharField(
        max_length=200,
        verbose_name=_("Twitter type"),
        blank=True,
        choices=get_setting("TWITTER_TYPES"),
        default=get_setting("TWITTER_TYPE"),
    )
    #: Twitter site handle (default: :ref:`TWITTER_SITE <TWITTER_SITE>`)
    twitter_site = models.CharField(
        max_length=200, verbose_name=_("Twitter site handle"), blank=True, default=get_setting("TWITTER_SITE")
    )
    #: Twitter author handle (default: :ref:`TWITTER_AUTHOR <TWITTER_AUTHOR>`)
    twitter_author = models.CharField(
        max_length=200, verbose_name=_("Twitter author handle"), blank=True, default=get_setting("TWITTER_AUTHOR")
    )
    #: Schema.org object type (default: :ref:`SCHEMAORG_TYPE <SCHEMAORG_TYPE>`)
    gplus_type = models.CharField(
        max_length=200,
        verbose_name=_("Schema.org type"),
        blank=True,
        choices=get_setting("SCHEMAORG_TYPES"),
        default=get_setting("SCHEMAORG_TYPE"),
    )
    #: Schema.org author name abstract field (default: :ref:`SCHEMAORG_AUTHOR <SCHEMAORG_AUTHOR>`)
    gplus_author = models.CharField(
        max_length=200, verbose_name=_("Schema.org author name"), blank=True, default=get_setting("SCHEMAORG_AUTHOR")
    )
    #: Send notifications on post update. Require channels integration
    send_knock_create = models.BooleanField(
        verbose_name=_("Send notifications on post publish"),
        default=False,
        help_text=_("Emits a desktop notification -if enabled- when publishing a new post"),
    )
    #: Send notifications on post update. Require channels integration
    send_knock_update = models.BooleanField(
        verbose_name=_("Send notifications on post update"),
        default=False,
        help_text=_("Emits a desktop notification -if enabled- when editing a published post"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Remove urlconf from form if no apphook-based url config is enabled"""
        if isinstance(get_setting("URLCONF"), str):
            self.fields["urlconf"].widget = forms.HiddenInput()
            self.fields["urlconf"].label = ""  # Admin otherwise displays label for hidden field

    def get_app_title(self):
        return getattr(self, "app_title", _("untitled"))

    @property
    def schemaorg_type(self):
        """Compatibility shim to fetch data from legacy gplus_type field."""
        return self.gplus_type

    def __str__(self):
        return f"{self.namespace}: {self.get_app_title()} / {self.object_name}"


def get_app_instance(request):
    app = None
    namespace, config = "", None
    if getattr(request, "current_page", None) and request.current_page.application_urls:
        app = apphook_pool.get_apphook(request.current_page.application_urls)
        print(f"--> {app}")
        if app and app.app_config:
            try:
                config = None
                with override(get_language_from_request(request, check_path=True)):
                    if hasattr(request, "toolbar") and hasattr(request.toolbar, "request_path"):
                        path = request.toolbar.request_path  # If v4 endpoint take request_path from toolbar
                    else:
                        path = request.path_info
                    namespace = resolve(path).namespace
                    config = app.get_config(namespace)
            except Resolver404:
                pass
    return namespace, config
