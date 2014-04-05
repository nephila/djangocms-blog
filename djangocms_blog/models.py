# -*- coding: utf-8 -*-
from cms.models import PlaceholderField, CMSPlugin
from cmsplugin_filer_image.models import ThumbnailOption
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _, get_language
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields
from parler.managers import TranslationManager
from taggit_autosuggest.managers import TaggableManager

from . import settings
from .managers import GenericDateTaggedManager

BLOG_CURRENT_POST_IDENTIFIER = 'djangocms_post_current'


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

    def __unicode__(self):
        return self.safe_translation_getter('name')

    def save(self, *args, **kwargs):
        super(BlogCategory, self).save(*args, **kwargs)
        for lang in self.get_available_languages():
            self.set_current_language(lang)
            if not self.slug and self.name:
                self.slug = slugify(self.name)
        self.save_translations()


class Post(TranslatableModel):
    """
    Blog post
    """
    author = models.ForeignKey(User, verbose_name=_('Author'), null=True, blank=True,
                               related_name='djangocms_blog_author')

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
                                 related_name='djangocmsblog_post_image')
    main_image_thumbnail = models.ForeignKey(ThumbnailOption,
                                             verbose_name=_('Main image thumbnail'),
                                             related_name='blog_post_thumbnail',
                                             blank=True, null=True)
    main_image_full = models.ForeignKey(ThumbnailOption,
                                        verbose_name=_('Main image full'),
                                        related_name='blog_post_full',
                                        blank=True, null=True)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.SlugField(_('slug'), blank=True, db_index=True),
        abstract=HTMLField(_('Text')),
        meta_description=models.TextField(verbose_name=_(u'Post meta description'),
                                          blank=True, default=''),
        meta_keywords=models.TextField(verbose_name=_(u'Post meta keywords'),
                                       blank=True, default=''),
        meta={'unique_together': (('language_code', 'slug'),)}
    )
    content = PlaceholderField("post_content")

    objects = GenericDateTaggedManager()
    tags = TaggableManager(blank=True, related_name='djangocms_blog_tags')

    class Meta:
        verbose_name = _('blog article')
        verbose_name_plural = _('blog articles')
        ordering = ("-date_published", "-date_created")
        get_latest_by = 'date_published'

    def __unicode__(self):
        return self.safe_translation_getter('title')

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)
        for lang in self.get_available_languages():
            self.set_current_language(lang)
            if not self.slug and self.title:
                self.slug = slugify(self.title)
        self.save_translations()

    def get_absolute_url(self):
        kwargs = {'year': self.date_published.year,
                  'month': self.date_published.month,
                  'day': self.date_published.day,
                  'slug': self.safe_translation_getter('slug', language_code=get_language())}
        return reverse('djangocms_blog:post-detail', kwargs=kwargs)

    def thumbnail_options(self):
        if self.main_image_thumbnail_id:
            return self.main_image_thumbnail.as_dict
        else:
            return settings.BLOG_IMAGE_THUMBNAIL_SIZE
        
    def get_full_url(self):
        s = Site.objects.get_current()
        if s.domain.find('http') > -1:
            return "%s%s" % (s.domain, self.get_absolute_url())
        else:
            return "http://%s%s" % (s.domain, self.get_absolute_url())

    def full_image_options(self):
        if self.main_image_fulll_id:
            return self.main_image_full.as_dict
        else:
            return settings.BLOG_IMAGE_FULL_SIZE


class LatestPostsPlugin(CMSPlugin):

    latest_posts = models.IntegerField(_(u'Articles'), default=settings.BLOG_LATEST_POSTS,
                                       help_text=_('The number of latests articles to be displayed.'))
    tags = models.ManyToManyField('taggit.Tag', blank=True,
                                  help_text=_('Show only the blog articles tagged with chosen tags.'))
    categories = models.ManyToManyField('BlogCategory', blank=True,
                                        help_text=_('Show only the blog articles tagged with chosen categories.'))

    def __unicode__(self):
        return u"%s latest articles by tag" % self.latest_posts

    def copy_relations(self, oldinstance):
        self.tags = oldinstance.tags.all()

    def get_posts(self):
        posts = Post.objects.published()
        tags = list(self.tags.all())
        if tags:
            posts = posts.filter(tags__in=tags)
        return posts[:self.latest_posts]


class AuthorEntriesPlugin(CMSPlugin):
    authors = models.ManyToManyField(User, verbose_name=_('Authors'),
                                     limit_choices_to={'post_set__publish': True}
                                     )
    latest_posts = models.IntegerField(_(u'Articles'), default=settings.BLOG_LATEST_POSTS,
                                       help_text=_('The number of author articles to be displayed.'))

    def __unicode__(self):
        return u"%s latest articles by author" % self.latest_posts

    def copy_relations(self, oldinstance):
        self.authors = oldinstance.authors.all()

    def get_posts(self):
        posts = (Post.objects.published().filter(author__in=self.authors.all()))
        return posts[:self.latest_posts]

    def get_authors(self):
        authors = self.authors.all()
        for author in authors:
            if author.post_set.filter(publish=True).exists():
                author.count = author.post_set.filter(publish=True).count()
        return authors
