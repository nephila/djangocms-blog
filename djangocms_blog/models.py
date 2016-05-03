# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import hashlib

from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_apphooks_config.managers.parler import AppHookConfigTranslatableManager
from cms.models import CMSPlugin, PlaceholderField
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text, python_2_unicode_compatible
from django.utils.html import escape, strip_tags
from django.utils.text import slugify
from django.utils.translation import get_language, ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from meta.models import ModelMeta
from parler.models import TranslatableModel, TranslatedFields
from parler.utils.context import switch_language
from taggit_autosuggest.managers import TaggableManager

from .cms_appconfig import BlogConfig
from .managers import GenericDateTaggedManager
from .settings import get_setting

BLOG_CURRENT_POST_IDENTIFIER = get_setting('CURRENT_POST_IDENTIFIER')
BLOG_CURRENT_NAMESPACE = get_setting('CURRENT_NAMESPACE')

try:
    from filer.models import ThumbnailOption  # NOQA
    thumbnail_model = 'filer.ThumbnailOption'
except ImportError:
    from cmsplugin_filer_image.models import ThumbnailOption  # NOQA
    thumbnail_model = 'cmsplugin_filer_image.ThumbnailOption'

try:
    from knocker.mixins import KnockerModel
except ImportError:
    class KnockerModel(object):
        """
        Stub class if django-knocker is not installed
        """
        pass


@python_2_unicode_compatible
class BlogCategory(TranslatableModel):
    """
    Blog category
    """
    parent = models.ForeignKey('self', verbose_name=_('parent'), null=True, blank=True)
    date_created = models.DateTimeField(_('created at'), auto_now_add=True)
    date_modified = models.DateTimeField(_('modified at'), auto_now=True)
    app_config = AppHookConfigField(
        BlogConfig, null=True, verbose_name=_('app. config')
    )

    translations = TranslatedFields(
        name=models.CharField(_('name'), max_length=255),
        slug=models.SlugField(_('slug'), max_length=255, blank=True, db_index=True),
        meta={'unique_together': (('language_code', 'slug'),)}
    )

    objects = AppHookConfigTranslatableManager()

    class Meta:
        verbose_name = _('blog category')
        verbose_name_plural = _('blog categories')

    @property
    def count(self):
        return self.blog_posts.namespace(self.app_config.namespace).published().count()

    def get_absolute_url(self, lang=None):
        if not lang:
            lang = get_language()
        if self.has_translation(lang, ):
            slug = self.safe_translation_getter('slug', language_code=lang)
            return reverse(
                '%s:posts-category' % self.app_config.namespace,
                kwargs={'category': slug},
                current_app=self.app_config.namespace
            )
        # in case category doesn't exist in this language, gracefully fallback
        # to posts-latest
        return reverse(
            '%s:posts-latest' % self.app_config.namespace, current_app=self.app_config.namespace
        )

    def __str__(self):
        return self.safe_translation_getter('name')

    def save(self, *args, **kwargs):
        super(BlogCategory, self).save(*args, **kwargs)
        for lang in self.get_available_languages():
            self.set_current_language(lang)
            if not self.slug and self.name:
                self.slug = slugify(force_text(self.name))
        self.save_translations()


@python_2_unicode_compatible
class Post(KnockerModel, ModelMeta, TranslatableModel):
    """
    Blog post
    """
    author = models.ForeignKey(dj_settings.AUTH_USER_MODEL,
                               verbose_name=_('author'), null=True, blank=True,
                               related_name='djangocms_blog_post_author')

    date_created = models.DateTimeField(_('created'), auto_now_add=True)
    date_modified = models.DateTimeField(_('last modified'), auto_now=True)
    date_published = models.DateTimeField(_('published since'), null=True, blank=True)
    date_published_end = models.DateTimeField(_('published until'), null=True, blank=True)
    publish = models.BooleanField(_('publish'), default=False)
    categories = models.ManyToManyField('djangocms_blog.BlogCategory', verbose_name=_('category'),
                                        related_name='blog_posts', blank=True)
    main_image = FilerImageField(verbose_name=_('main image'), blank=True, null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='djangocms_blog_post_image')
    main_image_thumbnail = models.ForeignKey(thumbnail_model,
                                             verbose_name=_('main image thumbnail'),
                                             related_name='djangocms_blog_post_thumbnail',
                                             on_delete=models.SET_NULL,
                                             blank=True, null=True)
    main_image_full = models.ForeignKey(thumbnail_model,
                                        verbose_name=_('main image full'),
                                        related_name='djangocms_blog_post_full',
                                        on_delete=models.SET_NULL,
                                        blank=True, null=True)
    enable_comments = models.BooleanField(verbose_name=_('enable comments on post'),
                                          default=get_setting('ENABLE_COMMENTS'))
    sites = models.ManyToManyField('sites.Site', verbose_name=_('Site(s)'), blank=True,
                                   help_text=_('Select sites in which to show the post. '
                                               'If none is set it will be '
                                               'visible in all the configured sites.'))
    app_config = AppHookConfigField(
        BlogConfig, null=True, verbose_name=_('app. config')
    )

    translations = TranslatedFields(
        title=models.CharField(_('title'), max_length=255),
        slug=models.SlugField(_('slug'), max_length=255, blank=True, db_index=True),
        abstract=HTMLField(_('abstract'), blank=True, default=''),
        meta_description=models.TextField(verbose_name=_('post meta description'),
                                          blank=True, default=''),
        meta_keywords=models.TextField(verbose_name=_('post meta keywords'),
                                       blank=True, default=''),
        meta_title=models.CharField(verbose_name=_('post meta title'),
                                    help_text=_('used in title tag and social sharing'),
                                    max_length=255,
                                    blank=True, default=''),
        post_text=HTMLField(_('text'), default='', blank=True),
        meta={'unique_together': (('language_code', 'slug'),)}
    )
    content = PlaceholderField('post_content', related_name='post_content')

    objects = GenericDateTaggedManager()
    tags = TaggableManager(blank=True, related_name='djangocms_blog_tags')

    _metadata = {
        'title': 'get_title',
        'description': 'get_description',
        'keywords': 'get_keywords',
        'og_description': 'get_description',
        'twitter_description': 'get_description',
        'gplus_description': 'get_description',
        'locale': 'get_locale',
        'image': 'get_image_full_url',
        'object_type': 'get_meta_attribute',
        'og_type': 'get_meta_attribute',
        'og_app_id': 'get_meta_attribute',
        'og_profile_id': 'get_meta_attribute',
        'og_publisher': 'get_meta_attribute',
        'og_author_url': 'get_meta_attribute',
        'og_author': 'get_meta_attribute',
        'twitter_type': 'get_meta_attribute',
        'twitter_site': 'get_meta_attribute',
        'twitter_author': 'get_meta_attribute',
        'gplus_type': 'get_meta_attribute',
        'gplus_author': 'get_meta_attribute',
        'published_time': 'date_published',
        'modified_time': 'date_modified',
        'expiration_time': 'date_published_end',
        'tag': 'get_tags',
        'url': 'get_absolute_url',
    }

    class Meta:
        verbose_name = _('blog article')
        verbose_name_plural = _('blog articles')
        ordering = ('-date_published', '-date_created')
        get_latest_by = 'date_published'

    def __str__(self):
        return self.safe_translation_getter('title')

    @property
    def guid(self, language=None):
        if not language:
            language = self.get_current_language()
        base_string = '{0}{2}{1}'.format(
            language, self.app_config.namespace,
            self.safe_translation_getter('slug', language_code=language, any_language=True)
        )
        return hashlib.sha256(force_bytes(base_string)).hexdigest()

    def save(self, *args, **kwargs):
        """
        Handle some auto configuration during save
        """
        if self.publish and self.date_published is None:
            self.date_published = timezone.now()
        super(Post, self).save(*args, **kwargs)

    def save_translation(self, translation, *args, **kwargs):
        """
        Handle some auto configuration during save
        """
        if not translation.slug and translation.title:
            translation.slug = slugify(translation.title)
        super(Post, self).save_translation(translation, *args, **kwargs)

    def get_absolute_url(self, lang=None):
        if not lang or lang not in self.get_available_languages():
            lang = self.get_current_language()
        if not lang or lang not in self.get_available_languages():
            lang = get_language()
        with switch_language(self, lang):
            category = self.categories.first()
            kwargs = {}
            if self.date_published:
                current_date = self.date_published
            else:
                current_date = self.date_created
            urlconf = get_setting('PERMALINK_URLS')[self.app_config.url_patterns]
            if '<year>' in urlconf:
                kwargs['year'] = current_date.year
            if '<month>' in urlconf:
                kwargs['month'] = '%02d' % current_date.month
            if '<day>' in urlconf:
                kwargs['day'] = '%02d' % current_date.day
            if '<slug>' in urlconf:
                kwargs['slug'] = self.safe_translation_getter('slug', language_code=lang, any_language=True)  # NOQA
            if '<category>' in urlconf:
                kwargs['category'] = category.safe_translation_getter('slug', language_code=lang, any_language=True)  # NOQA
            return reverse('%s:post-detail' % self.app_config.namespace, kwargs=kwargs)

    def get_meta_attribute(self, param):
        """
        Retrieves django-meta attributes from apphook config instance
        :param param: django-meta attribute passed as key
        """
        return self._get_meta_value(param, getattr(self.app_config, param)) or ''

    def get_title(self):
        title = self.safe_translation_getter('meta_title', any_language=True)
        if not title:
            title = self.safe_translation_getter('title', any_language=True)
        return title.strip()

    def get_keywords(self):
        """
        Returns the list of keywords (as python list)
        :return: list
        """
        return self.safe_translation_getter('meta_keywords', default='').strip().split(',')

    def get_locale(self):
        return self.get_current_language()

    def get_description(self):
        description = self.safe_translation_getter('meta_description', any_language=True)
        if not description:
            description = self.safe_translation_getter('abstract', any_language=True)
        return escape(strip_tags(description)).strip()

    def get_image_full_url(self):
        if self.main_image:
            return self.build_absolute_uri(self.main_image.url)
        return ''

    def get_tags(self):
        """
        Returns the list of object tags as comma separated list
        """
        taglist = [tag.name for tag in self.tags.all()]
        return ','.join(taglist)

    def get_author(self):
        """
        Return the author (user) objects
        """
        return self.author

    def _set_default_author(self, current_user):
        if not self.author_id and self.app_config.set_author:
            if get_setting('AUTHOR_DEFAULT') is True:
                user = current_user
            else:
                user = get_user_model().objects.get(username=get_setting('AUTHOR_DEFAULT'))
            self.author = user

    def thumbnail_options(self):
        if self.main_image_thumbnail_id:
            return self.main_image_thumbnail.as_dict
        else:
            return get_setting('IMAGE_THUMBNAIL_SIZE')

    def full_image_options(self):
        if self.main_image_full_id:
            return self.main_image_full.as_dict
        else:
            return get_setting('IMAGE_FULL_SIZE')

    def get_full_url(self):
        """
        Return the url with protocol and domain url
        """
        return self.build_absolute_uri(self.get_absolute_url())

    @property
    def is_published(self):
        """
        Checks wether the blog post is *really* published by checking publishing dates too
        """
        return (self.publish and
                (self.date_published and self.date_published <= timezone.now()) and
                (self.date_published_end is None or self.date_published_end > timezone.now())
                )

    def should_knock(self, created=False):
        """
        Returns whether to emit knocks according to the post state
        """
        new = (self.app_config.send_knock_create and self.is_published and
               self.date_published == self.date_modified)
        updated = self.app_config.send_knock_update and self.is_published
        return new or updated

    def get_cache_key(self, language, prefix):
        return 'djangocms-blog:{2}:{0}:{1}'.format(language, self.guid, prefix)


class BasePostPlugin(CMSPlugin):
    app_config = AppHookConfigField(
        BlogConfig, null=True, verbose_name=_('app. config'), blank=True
    )

    class Meta:
        abstract = True

    def post_queryset(self, request=None):
        language = get_language()
        posts = Post._default_manager
        if self.app_config:
            posts = posts.namespace(self.app_config.namespace)
        posts = posts.active_translations(language_code=language)
        if not request or not getattr(request, 'toolbar', False) or not request.toolbar.edit_mode:
            posts = posts.published()
        return posts.all()


@python_2_unicode_compatible
class LatestPostsPlugin(BasePostPlugin):
    latest_posts = models.IntegerField(_('articles'), default=get_setting('LATEST_POSTS'),
                                       help_text=_('The number of latests '
                                                   u'articles to be displayed.'))
    tags = TaggableManager(_('filter by tag'), blank=True,
                           help_text=_('Show only the blog articles tagged with chosen tags.'),
                           related_name='djangocms_blog_latest_post')
    categories = models.ManyToManyField('djangocms_blog.BlogCategory', blank=True,
                                        verbose_name=_('filter by category'),
                                        help_text=_('Show only the blog articles tagged '
                                                    u'with chosen categories.'))

    def __str__(self):
        return force_text(_('%s latest articles by tag') % self.latest_posts)

    def copy_relations(self, oldinstance):
        for tag in oldinstance.tags.all():
            self.tags.add(tag)
        for category in oldinstance.categories.all():
            self.categories.add(category)

    def get_posts(self, request):
        posts = self.post_queryset(request)
        if self.tags.exists():
            posts = posts.filter(tags__in=list(self.tags.all()))
        if self.categories.exists():
            posts = posts.filter(categories__in=list(self.categories.all()))
        return posts.distinct()[:self.latest_posts]


@python_2_unicode_compatible
class AuthorEntriesPlugin(BasePostPlugin):
    authors = models.ManyToManyField(
        dj_settings.AUTH_USER_MODEL, verbose_name=_('authors'),
        limit_choices_to={'djangocms_blog_post_author__publish': True}
    )
    latest_posts = models.IntegerField(
        _('articles'), default=get_setting('LATEST_POSTS'),
        help_text=_('The number of author articles to be displayed.')
    )

    def __str__(self):
        return force_text(_('%s latest articles by author') % self.latest_posts)

    def copy_relations(self, oldinstance):
        self.authors = oldinstance.authors.all()

    def get_posts(self, request):
        posts = self.post_queryset(request)
        return posts[:self.latest_posts]

    def get_authors(self):
        authors = self.authors.all()
        for author in authors:
            author.count = 0
            qs = author.djangocms_blog_post_author
            if self.app_config:
                qs = qs.namespace(self.app_config.namespace)
            count = qs.filter(publish=True).count()
            if count:
                author.count = count
        return authors


@python_2_unicode_compatible
class GenericBlogPlugin(BasePostPlugin):

    class Meta:
        abstract = False

    def __str__(self):
        return force_text(_('generic blog plugin'))


@receiver(pre_delete, sender=Post)
def pre_delete_post(sender, instance, **kwargs):
    for language in instance.get_available_languages():
        key = instance.get_cache_key(language, 'feed')
        cache.delete(key)


@receiver(post_save, sender=Post)
def post_save_post(sender, instance, **kwargs):
    for language in instance.get_available_languages():
        key = instance.get_cache_key(language, 'feed')
        cache.delete(key)
