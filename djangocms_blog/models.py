# -*- coding: utf-8 -*-
from cms.models import PlaceholderField, CMSPlugin
from cmsplugin_filer_image.models import ThumbnailOption
from django.conf import settings as dj_settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import strip_tags, escape
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _, get_language
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from meta_mixin.models import ModelMeta
from parler.models import TranslatableModel, TranslatedFields
from parler.managers import TranslationManager
from taggit_autosuggest.managers import TaggableManager

from .settings import get_setting
from .managers import GenericDateTaggedManager

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
        return self.blog_posts.filter(publish=True).count()

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
                               verbose_name=_('Author'), null=True, blank=True,
                               related_name='djangocms_blog_post_author')

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_published = models.DateTimeField(_('Published Since'),
                                          default=timezone.now)
    date_published_end = models.DateTimeField(_('Published Until'), null=True,
                                              blank=True)
    publish = models.BooleanField(_('Publish'), default=False)
    categories = models.ManyToManyField(BlogCategory, verbose_name=_('category'),
                                        related_name='blog_posts',)
    main_image = FilerImageField(verbose_name=_('Main image'), blank=True, null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='djangocms_blog_post_image')
    main_image_thumbnail = models.ForeignKey(ThumbnailOption,
                                             verbose_name=_('Main image thumbnail'),
                                             related_name='djangocms_blog_post_thumbnail',
                                             on_delete=models.SET_NULL,
                                             blank=True, null=True)
    main_image_full = models.ForeignKey(ThumbnailOption,
                                        verbose_name=_('Main image full'),
                                        related_name='djangocms_blog_post_full',
                                        on_delete=models.SET_NULL,
                                        blank=True, null=True)
    enable_comments = models.BooleanField(
        verbose_name=_(u'Enable comments on post'),
        default=get_setting('ENABLE_COMMENTS')
    )
    sites = models.ManyToManyField(Site, verbose_name=_(u'Site(s)'), blank=True,
                                   null=True,
                                   help_text=_(u'Select sites in which to show the post. '
                                               u'If none is set it will be '
                                               u'visible in all the configured sites.')
                                   )

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.SlugField(_('slug'), blank=True, db_index=True),
        abstract=HTMLField(_('Abstract')),
        meta_description=models.TextField(verbose_name=_(u'Post meta description'),
                                          blank=True, default=''),
        meta_keywords=models.TextField(verbose_name=_(u'Post meta keywords'),
                                       blank=True, default=''),
        meta_title=models.CharField(verbose_name=_(u'Post meta title'),
                                    help_text=_(u'used in title tag and social sharing'),
                                    max_length=255,
                                    blank=True, default=''),
        post_text=HTMLField(_('Text'), default='', blank=True),
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

    class Meta:
        verbose_name = _('blog article')
        verbose_name_plural = _('blog articles')
        ordering = ('-date_published', '-date_created')
        get_latest_by = 'date_published'

    def __str__(self):
        return self.safe_translation_getter('title')

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)
        main_lang = self.get_current_language()
        for lang in self.get_available_languages():
            self.set_current_language(lang)
            if not self.slug and self.title:
                self.slug = slugify(self.title)
        self.set_current_language(main_lang)
        self.save_translations()

    def get_absolute_url(self):
        kwargs = {'year': self.date_published.year,
                  'month': '%02d' % self.date_published.month,
                  'day': '%02d' % self.date_published.day,
                  'slug': self.safe_translation_getter('slug',
                                                       language_code=get_language(),
                                                       any_language=True)}
        return reverse('djangocms_blog:post-detail', kwargs=kwargs)

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
        return unicode(self.latest_posts)


class LatestPostsPlugin(BasePostPlugin):

    latest_posts = models.IntegerField(_(u'Articles'), default=get_setting('LATEST_POSTS'),
                                       help_text=_('The number of latests articles to be displayed.'))
    tags = models.ManyToManyField('taggit.Tag', blank=True,
                                  help_text=_('Show only the blog articles tagged with chosen tags.'))
    categories = models.ManyToManyField('BlogCategory', blank=True,
                                        help_text=_('Show only the blog articles tagged with chosen categories.'))

    def __str__(self):
        return u'%s latest articles by tag' % self.latest_posts

    def copy_relations(self, oldinstance):
        self.tags = oldinstance.tags.all()

    def get_posts(self, request):
        posts = self.post_queryset(request)
        tags = list(self.tags.all())
        if tags:
            posts = posts.filter(tags__in=tags)
        return posts[:self.latest_posts]


class AuthorEntriesPlugin(BasePostPlugin):
    authors = models.ManyToManyField(
        dj_settings.AUTH_USER_MODEL, verbose_name=_('Authors'),
        limit_choices_to={'djangocms_blog_post_author__publish': True}
    )
    latest_posts = models.IntegerField(
        _(u'Articles'), default=get_setting('LATEST_POSTS'),
        help_text=_('The number of author articles to be displayed.')
    )

    def __str__(self):
        return u'%s latest articles by author' % self.latest_posts

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
