import hashlib

from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_apphooks_config.managers.parler import AppHookConfigTranslatableManager
from cms.models import CMSPlugin, PlaceholderField
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.functional import cached_property
from django.utils.html import escape, strip_tags
from django.utils.translation import get_language, gettext, gettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from filer.models import ThumbnailOption
from meta.models import ModelMeta
from parler.models import TranslatableModel, TranslatedFields
from parler.utils.context import switch_language
from sortedm2m.fields import SortedManyToManyField
from taggit_autosuggest.managers import TaggableManager

from .cms_appconfig import BlogConfig
from .fields import slugify
from .managers import GenericDateTaggedManager
from .settings import get_setting

BLOG_CURRENT_POST_IDENTIFIER = get_setting("CURRENT_POST_IDENTIFIER")
BLOG_CURRENT_NAMESPACE = get_setting("CURRENT_NAMESPACE")
BLOG_PLUGIN_TEMPLATE_FOLDERS = get_setting("PLUGIN_TEMPLATE_FOLDERS")


thumbnail_model = "{}.{}".format(ThumbnailOption._meta.app_label, ThumbnailOption.__name__)


try:
    from knocker.mixins import KnockerModel
except ImportError:  # pragma: no cover

    class KnockerModel:
        """
        Stub class if django-knocker is not installed
        """

        pass


def _get_language(instance, language):
    available_languages = instance.get_available_languages()
    if language and language in available_languages:
        return language
    language = get_language()
    if language and language in available_languages:
        return language
    language = instance.get_current_language()
    if language and language in available_languages:
        return language
    if get_setting("USE_FALLBACK_LANGUAGE_IN_URL"):
        for fallback_language in instance.get_fallback_languages():
            if fallback_language in available_languages:
                return fallback_language
    return language


class BlogMetaMixin(ModelMeta):
    def get_meta_attribute(self, param):
        """
        Retrieves django-meta attributes from apphook config instance
        :param param: django-meta attribute passed as key
        """
        return self._get_meta_value(param, getattr(self.app_config, param)) or ""

    def get_locale(self):
        return self.get_current_language()

    def get_full_url(self):
        """
        Return the url with protocol and domain url
        """
        return self.build_absolute_uri(self.get_absolute_url())


class BlogCategory(BlogMetaMixin, TranslatableModel):
    """
    Blog category
    """

    parent = models.ForeignKey(
        "self", verbose_name=_("parent"), null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(_("created at"), auto_now_add=True)
    date_modified = models.DateTimeField(_("modified at"), auto_now=True)
    app_config = AppHookConfigField(BlogConfig, null=True, verbose_name=_("app. config"))

    translations = TranslatedFields(
        name=models.CharField(_("name"), max_length=752),
        slug=models.SlugField(_("slug"), max_length=752, blank=True, db_index=True),
        meta_description=models.TextField(verbose_name=_("category meta description"), blank=True, default=""),
        meta={"unique_together": (("language_code", "slug"),)},
    )

    objects = AppHookConfigTranslatableManager()

    _metadata = {
        "title": "get_title",
        "description": "get_description",
        "og_description": "get_description",
        "twitter_description": "get_description",
        "schemaorg_description": "get_description",
        "schemaorg_type": "get_meta_attribute",
        "locale": "get_locale",
        "object_type": "get_meta_attribute",
        "og_type": "get_meta_attribute",
        "og_app_id": "get_meta_attribute",
        "og_profile_id": "get_meta_attribute",
        "og_publisher": "get_meta_attribute",
        "og_author_url": "get_meta_attribute",
        "og_author": "get_meta_attribute",
        "twitter_type": "get_meta_attribute",
        "twitter_site": "get_meta_attribute",
        "twitter_author": "get_meta_attribute",
        "url": "get_absolute_url",
    }

    class Meta:
        verbose_name = _("blog category")
        verbose_name_plural = _("blog categories")

    def descendants(self):
        children = []
        if self.children.exists():
            children.extend(self.children.all())
            for child in self.children.all():
                children.extend(child.descendants())
        return children

    @cached_property
    def linked_posts(self):
        return self.blog_posts.namespace(self.app_config.namespace)

    @cached_property
    def count(self):
        return self.linked_posts.published().count()

    @cached_property
    def count_all_sites(self):
        return self.linked_posts.published(current_site=False).count()

    def get_absolute_url(self, lang=None):
        lang = _get_language(self, lang)
        if self.has_translation(lang):
            slug = self.safe_translation_getter("slug", language_code=lang)
            return reverse(
                "%s:posts-category" % self.app_config.namespace,
                kwargs={"category": slug},
                current_app=self.app_config.namespace,
            )
        # in case category doesn't exist in this language, gracefully fallback
        # to posts-latest
        return reverse("%s:posts-latest" % self.app_config.namespace, current_app=self.app_config.namespace)

    def __str__(self):
        default = gettext("BlogCategory (no translation)")
        return self.safe_translation_getter("name", any_language=True, default=default)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for lang in self.get_available_languages():
            self.set_current_language(lang)
            if not self.slug and self.name:
                self.slug = slugify(force_str(self.name))
        self.save_translations()

    def get_title(self):
        title = self.safe_translation_getter("name", any_language=True)
        return title.strip()

    def get_description(self):
        description = self.safe_translation_getter("meta_description", any_language=True)
        return escape(strip_tags(description)).strip()


class Post(KnockerModel, BlogMetaMixin, TranslatableModel):
    """
    Blog post
    """

    author = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        null=True,
        blank=True,
        related_name="djangocms_blog_post_author",
        on_delete=models.PROTECT,
    )

    date_created = models.DateTimeField(_("created"), auto_now_add=True)
    date_modified = models.DateTimeField(_("last modified"), auto_now=True)
    date_published = models.DateTimeField(_("published since"), null=True, blank=True)
    date_published_end = models.DateTimeField(_("published until"), null=True, blank=True)
    date_featured = models.DateTimeField(_("featured date"), null=True, blank=True)
    publish = models.BooleanField(_("publish"), default=False)
    categories = models.ManyToManyField(
        "djangocms_blog.BlogCategory", verbose_name=_("category"), related_name="blog_posts", blank=True
    )
    main_image = FilerImageField(
        verbose_name=_("main image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="djangocms_blog_post_image",
    )
    main_image_thumbnail = models.ForeignKey(
        thumbnail_model,
        verbose_name=_("main image thumbnail"),
        related_name="djangocms_blog_post_thumbnail",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    main_image_full = models.ForeignKey(
        thumbnail_model,
        verbose_name=_("main image full"),
        related_name="djangocms_blog_post_full",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    enable_comments = models.BooleanField(
        verbose_name=_("enable comments on post"), default=get_setting("ENABLE_COMMENTS")
    )
    sites = models.ManyToManyField(
        "sites.Site",
        verbose_name=_("Site(s)"),
        blank=True,
        help_text=_(
            "Select sites in which to show the post. "
            "If none is set it will be "
            "visible in all the configured sites."
        ),
    )
    app_config = AppHookConfigField(BlogConfig, null=True, verbose_name=_("app. config"))

    translations = TranslatedFields(
        title=models.CharField(_("title"), max_length=752),
        slug=models.SlugField(_("slug"), max_length=752, blank=True, db_index=True, allow_unicode=True),
        subtitle=models.CharField(verbose_name=_("subtitle"), max_length=767, blank=True, default=""),
        abstract=HTMLField(_("abstract"), blank=True, default="", configuration="BLOG_ABSTRACT_CKEDITOR"),
        meta_description=models.TextField(verbose_name=_("post meta description"), blank=True, default=""),
        meta_keywords=models.TextField(verbose_name=_("post meta keywords"), blank=True, default=""),
        meta_title=models.CharField(
            verbose_name=_("post meta title"),
            help_text=_("used in title tag and social sharing"),
            max_length=2000,
            blank=True,
            default="",
        ),
        post_text=HTMLField(_("text"), default="", blank=True, configuration="BLOG_POST_TEXT_CKEDITOR"),
        meta={"unique_together": (("language_code", "slug"),)},
    )
    media = PlaceholderField("media", related_name="media")
    content = PlaceholderField("post_content", related_name="post_content")
    liveblog = PlaceholderField("live_blog", related_name="live_blog")
    enable_liveblog = models.BooleanField(verbose_name=_("enable liveblog on post"), default=False)

    objects = GenericDateTaggedManager()
    tags = TaggableManager(
        blank=True,
        related_name="djangocms_blog_tags",
        help_text=_("Type a tag and hit tab, or start typing and select from autocomplete list."),
    )

    related = SortedManyToManyField("self", verbose_name=_("Related Posts"), blank=True, symmetrical=False)

    _metadata = {
        "title": "get_title",
        "description": "get_description",
        "keywords": "get_keywords",
        "og_description": "get_description",
        "twitter_description": "get_description",
        "schemaorg_description": "get_description",
        "locale": "get_locale",
        "image": "get_image_full_url",
        "image_width": "get_image_width",
        "image_height": "get_image_height",
        "object_type": "get_meta_attribute",
        "og_type": "get_meta_attribute",
        "og_app_id": "get_meta_attribute",
        "og_profile_id": "get_meta_attribute",
        "og_publisher": "get_meta_attribute",
        "og_author_url": "get_meta_attribute",
        "og_author": "get_meta_attribute",
        "twitter_type": "get_meta_attribute",
        "twitter_site": "get_meta_attribute",
        "twitter_author": "get_meta_attribute",
        "schemaorg_type": "get_meta_attribute",
        "published_time": "date_published",
        "modified_time": "date_modified",
        "expiration_time": "date_published_end",
        "tag": "get_tags",
        "url": "get_absolute_url",
    }

    class Meta:
        verbose_name = _("blog article")
        verbose_name_plural = _("blog articles")
        ordering = ("-date_published", "-date_created")
        get_latest_by = "date_published"

    def __str__(self):
        default = gettext("Post (no translation)")
        return self.safe_translation_getter("title", any_language=True, default=default)

    @property
    def guid(self, language=None):
        if not language:
            language = self.get_current_language()
        base_string = "-{0}-{2}-{1}-".format(
            language,
            self.app_config.namespace,
            self.safe_translation_getter("slug", language_code=language, any_language=True),
        )
        return hashlib.sha256(force_bytes(base_string)).hexdigest()

    @property
    def date(self):
        if self.date_featured:
            return self.date_featured
        return self.date_published

    def save(self, *args, **kwargs):
        """
        Handle some auto configuration during save
        """
        if self.publish and self.date_published is None:
            self.date_published = timezone.now()
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def save_translation(self, translation, *args, **kwargs):
        """
        Handle some auto configuration during save
        """
        if not translation.slug and translation.title:
            translation.slug = slugify(translation.title)
        super().save_translation(translation, *args, **kwargs)

    def get_absolute_url(self, lang=None):
        lang = _get_language(self, lang)
        with switch_language(self, lang):
            category = self.categories.first()
            kwargs = {}
            if self.date_published:
                current_date = self.date_published
            else:
                current_date = self.date_created
            urlconf = get_setting("PERMALINK_URLS")[self.app_config.url_patterns]
            if "<int:year>" in urlconf:
                kwargs["year"] = current_date.year
            if "<int:month>" in urlconf:
                kwargs["month"] = "%02d" % current_date.month
            if "<int:day>" in urlconf:
                kwargs["day"] = "%02d" % current_date.day
            if "<str:slug>" in urlconf or "<slug:slug>" in urlconf:
                kwargs["slug"] = self.safe_translation_getter("slug", language_code=lang, any_language=True)  # NOQA
            if "<slug:category>" in urlconf or "<str:category>" in urlconf:
                kwargs["category"] = category.safe_translation_getter(
                    "slug", language_code=lang, any_language=True
                )  # NOQA
            return reverse(
                "%s:post-detail" % self.app_config.namespace, kwargs=kwargs, current_app=self.app_config.namespace
            )

    def get_title(self):
        title = self.safe_translation_getter("meta_title", any_language=True)
        if not title:
            title = self.safe_translation_getter("title", any_language=True)
        return title.strip()

    def get_keywords(self):
        """
        Returns the list of keywords (as python list)
        :return: list
        """
        return self.safe_translation_getter("meta_keywords", default="").strip().split(",")

    def get_description(self):
        description = self.safe_translation_getter("meta_description", any_language=True)
        if not description:
            description = self.safe_translation_getter("abstract", any_language=True)
        return escape(strip_tags(description)).strip()

    def get_image_full_url(self):
        if self.main_image:
            return self.build_absolute_uri(self.main_image.url)
        return ""

    def get_image_width(self):
        if self.main_image:
            return self.main_image.width

    def get_image_height(self):
        if self.main_image:
            return self.main_image.height

    def get_tags(self):
        """
        Returns the list of object tags as comma separated list
        """
        taglist = [tag.name for tag in self.tags.all()]
        return ",".join(taglist)

    def get_author(self):
        """
        Return the author (user) objects
        """
        return self.author

    def _set_default_author(self, current_user):
        if not self.author_id and self.app_config.set_author:
            if get_setting("AUTHOR_DEFAULT") is True:
                user = current_user
            else:
                user = get_user_model().objects.get(username=get_setting("AUTHOR_DEFAULT"))
            self.author = user

    def thumbnail_options(self):
        if self.main_image_thumbnail_id:
            return self.main_image_thumbnail.as_dict
        else:
            return get_setting("IMAGE_THUMBNAIL_SIZE")

    def full_image_options(self):
        if self.main_image_full_id:
            return self.main_image_full.as_dict
        else:
            return get_setting("IMAGE_FULL_SIZE")

    @property
    def is_published(self):
        """
        Checks wether the blog post is *really* published by checking publishing dates too
        """
        return (
            self.publish
            and (self.date_published and self.date_published <= timezone.now())
            and (self.date_published_end is None or self.date_published_end > timezone.now())
        )

    def should_knock(self, signal_type, created=False):
        """
        Returns whether to emit knocks according to the post state
        """
        new = self.app_config.send_knock_create and self.is_published and self.date_published == self.date_modified
        updated = self.app_config.send_knock_update and self.is_published
        return (new or updated) and signal_type in ("post_save", "post_delete")

    def get_cache_key(self, language, prefix):
        return "djangocms-blog:{2}:{0}:{1}".format(language, self.guid, prefix)

    @property
    def liveblog_group(self):
        return "liveblog-{apphook}-{lang}-{post}".format(
            lang=self.get_current_language(),
            apphook=self.app_config.namespace,
            post=self.safe_translation_getter("slug", any_language=True),
        )


class BasePostPlugin(CMSPlugin):
    app_config = AppHookConfigField(BlogConfig, null=True, verbose_name=_("app. config"), blank=True)
    current_site = models.BooleanField(
        _("current site"), default=True, help_text=_("Select items from the current site only")
    )
    template_folder = models.CharField(
        max_length=200,
        verbose_name=_("Plugin template"),
        help_text=_("Select plugin template to load for this instance"),
        default=BLOG_PLUGIN_TEMPLATE_FOLDERS[0][0],
        choices=BLOG_PLUGIN_TEMPLATE_FOLDERS,
    )

    class Meta:
        abstract = True

    def optimize(self, qs):
        """
        Apply select_related / prefetch_related to optimize the view queries
        :param qs: queryset to optimize
        :return: optimized queryset
        """
        return qs.select_related("app_config").prefetch_related(
            "translations", "categories", "categories__translations", "categories__app_config"
        )

    def post_queryset(self, request=None, published_only=True):
        language = get_language()
        posts = Post.objects
        if self.app_config:
            posts = posts.namespace(self.app_config.namespace)
        if self.current_site:
            posts = posts.on_site(get_current_site(request))
        posts = posts.active_translations(language_code=language)
        if (
            published_only
            or not request
            or not getattr(request, "toolbar", False)
            or not request.toolbar.edit_mode_active
        ):
            posts = posts.published(current_site=self.current_site)
        return self.optimize(posts.all())


class LatestPostsPlugin(BasePostPlugin):
    latest_posts = models.IntegerField(
        _("articles"),
        default=get_setting("LATEST_POSTS"),
        help_text=_("The number of latests " "articles to be displayed."),
    )
    tags = TaggableManager(
        _("filter by tag"),
        blank=True,
        help_text=_("Show only the blog articles tagged with chosen tags."),
        related_name="djangocms_blog_latest_post",
    )
    categories = models.ManyToManyField(
        "djangocms_blog.BlogCategory",
        blank=True,
        verbose_name=_("filter by category"),
        help_text=_("Show only the blog articles tagged " "with chosen categories."),
    )

    def __str__(self):
        return force_str(_("%s latest articles by tag") % self.latest_posts)

    def copy_relations(self, oldinstance):
        for tag in oldinstance.tags.all():
            self.tags.add(tag)
        for category in oldinstance.categories.all():
            self.categories.add(category)

    def get_posts(self, request, published_only=True):
        posts = self.post_queryset(request, published_only)
        if self.tags.exists():
            posts = posts.filter(tags__in=list(self.tags.all()))
        if self.categories.exists():
            posts = posts.filter(categories__in=list(self.categories.all()))
        return self.optimize(posts.distinct())[: self.latest_posts]


class AuthorEntriesPlugin(BasePostPlugin):
    authors = models.ManyToManyField(
        dj_settings.AUTH_USER_MODEL,
        verbose_name=_("authors"),
        limit_choices_to={"djangocms_blog_post_author__publish": True},
    )
    latest_posts = models.IntegerField(
        _("articles"),
        default=get_setting("LATEST_POSTS"),
        help_text=_("The number of author articles to be displayed."),
    )

    def __str__(self):
        return force_str(_("%s latest articles by author") % self.latest_posts)

    def copy_relations(self, oldinstance):
        self.authors.set(oldinstance.authors.all())

    def get_posts(self, request, published_only=True):
        posts = self.post_queryset(request, published_only)
        return posts

    def get_authors(self, request):
        authors = self.authors.all()
        for author in authors:
            qs = self.get_posts(request).filter(author=author)
            # total nb of articles
            author.count = qs.count()
            # "the number of author articles to be displayed"
            author.posts = qs[: self.latest_posts]
        return authors


class GenericBlogPlugin(BasePostPlugin):
    class Meta:
        abstract = False

    def __str__(self):
        return force_str(_("generic blog plugin"))


@receiver(pre_delete, sender=Post)
def pre_delete_post(sender, instance, **kwargs):
    for language in instance.get_available_languages():
        key = instance.get_cache_key(language, "feed")
        cache.delete(key)


@receiver(post_save, sender=Post)
def post_save_post(sender, instance, **kwargs):
    for language in instance.get_available_languages():
        key = instance.get_cache_key(language, "feed")
        cache.delete(key)
