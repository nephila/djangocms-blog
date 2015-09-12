# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.models import CMSPlugin, PlaceholderField
from django.conf import settings as dj_settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import escape, strip_tags
from django.utils.text import slugify
from django.utils.translation import get_language, ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from meta_mixin.models import ModelMeta
from parler.managers import TranslationManager
from parler.models import TranslatableModel, TranslatedFields
from taggit_autosuggest.managers import TaggableManager

from .managers import GenericDateTaggedManager
from .settings import get_setting

BLOG_CURRENT_POST_IDENTIFIER = 'djangocms_post_current'


@python_2_unicode_compatible
class BlogCategory(TranslatableModel):
    """
    Blog category
    """
    parent = models.ForeignKey('self', verbose_name=_('parent'), null=True,
                               blank=True)
    date_created = models.DateTimeField(_('created at'), auto_now_add=True)
    date_modified = models.DateTimeField(_('modified at'), auto_now=True)

    translations = TranslatedFields(
        name=models.CharField(_('name'), max_length=255),
        slug=models.SlugField(_('slug'), blank=True, db_index=True),
        meta={'unique_together': (('language_code', 'slug'),)}
    )

    objects = TranslationManager()

    class Meta:
        verbose_name = _('blog category')
        verbose_name_plural = _('blog categories')

    @property
    def count(self):
        return self.blog_posts.published().count()

    def get_absolute_url(self):
        lang = get_language()
        if self.has_translation(lang):
            slug = self.safe_translation_getter('slug', language_code=lang)
            return reverse('djangocms_blog:posts-category', kwargs={'category': slug})
        # in case category doesn't exist in this language, gracefully fallback
        # to posts-latest
        return reverse('djangocms_blog:posts-latest')

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
class Post(ModelMeta, TranslatableModel):
    """
    Blog post
    """
    author = models.ForeignKey(dj_settings.AUTH_USER_MODEL,
                               verbose_name=_('author'), null=True, blank=True,
                               related_name='djangocms_blog_post_author')

    date_created = models.DateTimeField(_('created'), auto_now_add=True)
    date_modified = models.DateTimeField(_('last modified'), auto_now=True)
    date_published = models.DateTimeField(_('published Since'),
                                          default=timezone.now)
    date_published_end = models.DateTimeField(_('published Until'), null=True,
                                              blank=True)
    publish = models.BooleanField(_('publish'), default=False)
    categories = models.ManyToManyField('djangocms_blog.BlogCategory', verbose_name=_('category'),
                                        related_name='blog_posts',)
    main_image = FilerImageField(verbose_name=_('main image'), blank=True, null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='djangocms_blog_post_image')
    main_image_thumbnail = models.ForeignKey('cmsplugin_filer_image.ThumbnailOption',
                                             verbose_name=_('main image thumbnail'),
                                             related_name='djangocms_blog_post_thumbnail',
                                             on_delete=models.SET_NULL,
                                             blank=True, null=True)
    main_image_full = models.ForeignKey('cmsplugin_filer_image.ThumbnailOption',
                                        verbose_name=_('main image full'),
                                        related_name='djangocms_blog_post_full',
                                        on_delete=models.SET_NULL,
                                        blank=True, null=True)
    enable_comments = models.BooleanField(verbose_name=_('enable comments on post'),
                                          default=get_setting('ENABLE_COMMENTS'))
    sites = models.ManyToManyField('sites.Site', verbose_name=_('Site(s)'), blank=True,
                                   null=True,
                                   help_text=_('Select sites in which to show the post. '
                                               u'If none is set it will be '
                                               u'visible in all the configured sites.'))

    translations = TranslatedFields(
        title=models.CharField(_('title'), max_length=255),
        slug=models.SlugField(_('slug'), blank=True, db_index=True),
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
        'og_description': 'get_description',
        'twitter_description': 'get_description',
        'gplus_description': 'get_description',
        'keywords': 'get_keywords',
        'locale': None,
        'image': 'get_image_full_url',
        'object_type': get_setting('TYPE'),
        'og_type': get_setting('FB_TYPE'),
        'og_app_id': get_setting('FB_APPID'),
        'og_profile_id': get_setting('FB_PROFILE_ID'),
        'og_publisher': get_setting('FB_PUBLISHER'),
        'og_author_url': get_setting('FB_AUTHOR_URL'),
        'twitter_type': get_setting('TWITTER_TYPE'),
        'twitter_site': get_setting('TWITTER_SITE'),
        'twitter_author': get_setting('TWITTER_AUTHOR'),
        'gplus_type': get_setting('GPLUS_TYPE'),
        'gplus_author': get_setting('GPLUS_AUTHOR'),
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

    def get_absolute_url(self):
        kwargs = {'year': self.date_published.year,
                  'month': '%02d' % self.date_published.month,
                  'day': '%02d' % self.date_published.day,
                  'slug': self.safe_translation_getter('slug',
                                                       language_code=get_language(),
                                                       any_language=True)}
        return reverse('djangocms_blog:post-detail', kwargs=kwargs)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def get_title(self):
        title = self.safe_translation_getter('meta_title', any_language=True)
        if not title:
            title = self.safe_translation_getter('title', any_language=True)
        return title.strip()

    def get_keywords(self):
        return self.safe_translation_getter('meta_keywords').strip().split(',')

    def get_description(self):
        description = self.safe_translation_getter('meta_description', any_language=True)
        if not description:
            description = self.safe_translation_getter('abstract', any_language=True)
        return escape(strip_tags(description)).strip()

    def get_image_full_url(self):
        if self.main_image:
            return self.make_full_url(self.main_image.url)
        return ''

    def get_tags(self):
        taglist = [tag.name for tag in self.tags.all()]
        return ','.join(taglist)

    def get_author(self):
        return self.author

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
        return self.make_full_url(self.get_absolute_url())


@python_2_unicode_compatible
class BasePostPlugin(CMSPlugin):

    class Meta:
        abstract = True

    def post_queryset(self, request=None):
        language = get_language()
        posts = Post._default_manager.active_translations(language_code=language)
        if not request or not getattr(request, 'toolbar', False) or not request.toolbar.edit_mode:
            posts = posts.published()
        return posts

    def __str__(self):
        return force_text(self.latest_posts)


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
        return _('%s latest articles by tag') % self.latest_posts

    def copy_relations(self, oldinstance):
        for tag in oldinstance.tags.all():
            self.tags.add(tag)

    def get_posts(self, request):
        posts = self.post_queryset(request)
        if self.tags.exists():
            posts = posts.filter(tags__in=list(self.tags.all()))
        if self.categories.exists():
            posts = posts.filter(categories__in=list(self.categories.all()))
        return posts.distinct()[:self.latest_posts]


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
        return _('%s latest articles by author') % self.latest_posts

    def copy_relations(self, oldinstance):
        self.authors = oldinstance.authors.all()

    def get_posts(self, request):
        posts = self.post_queryset(request)
        return posts[:self.latest_posts]

    def get_authors(self):
        authors = self.authors.all()
        for author in authors:
            author.count = 0
            if author.djangocms_blog_post_author.filter(publish=True).exists():
                author.count = author.djangocms_blog_post_author.filter(publish=True).count()
        return authors
