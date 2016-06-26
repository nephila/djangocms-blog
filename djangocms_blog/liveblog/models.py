# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json

from channels import Group
from cms.models import CMSPlugin, python_2_unicode_compatible
from cms.utils.plugins import reorder_plugins
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.models import AbstractText
from filer.fields.image import FilerImageField

from djangocms_blog.models import Post, thumbnail_model

DATE_FORMAT = "%a %d %b %Y %H:%M"


@python_2_unicode_compatible
class LiveblogInterface(models.Model):
    """
    Abstract Liveblog plugin model, reusable to customize the liveblogging plugins.

    When implementing this, you **must** call ``self._post_save()`` in the concrete
    plugin model ``save`` method.
    """
    publish = models.BooleanField(_('publish liveblog entry'), default=False)
    node_order_by = '-changed_date'

    class Meta:
        verbose_name = _('liveblog entry')
        verbose_name_plural = _('liveblog entries')
        abstract = True

    def __str__(self):
        return str(self.pk)

    def _post_save(self):
        if self.publish:
            self.send()
        order = CMSPlugin.objects.filter(
            placeholder=self.placeholder
        ).order_by('placeholder', 'path').values_list('pk', flat=True)
        reorder_plugins(self.placeholder, None, self.language, order)

    @property
    def liveblog_group(self):
        post = Post.objects.language(self.language).filter(liveblog=self.placeholder).first()
        if post:
            return post.liveblog_group

    def render(self):
        return self.render_plugin()

    def send(self):
        """
        Render the content and send to the related group
        """
        if self.liveblog_group:
            notification = {
                'id': self.pk,
                'content': self.render(),
                'creation_date': self.creation_date.strftime(DATE_FORMAT),
                'changed_date': self.changed_date.strftime(DATE_FORMAT),
            }
            Group(self.liveblog_group).send({
                'text': json.dumps(notification),
            })


class Liveblog(LiveblogInterface, AbstractText):
    """
    Basic liveblog plugin model
    """
    title = models.CharField(_('title'), max_length=255)
    image = FilerImageField(
        verbose_name=_('image'), blank=True, null=True, on_delete=models.SET_NULL,
        related_name='djangocms_blog_liveblog_image'
    )
    thumbnail = models.ForeignKey(
        thumbnail_model, verbose_name=_('thumbnail size'), on_delete=models.SET_NULL,
        blank=True, null=True, related_name='djangocms_blog_liveblog_thumbnail'
    )

    class Meta:
        verbose_name = _('liveblog entry')
        verbose_name_plural = _('liveblog entries')

    def save(self, *args, **kwargs):
        super(Liveblog, self).save(*args, **kwargs)
        self._post_save()

    def __str__(self):
        return AbstractText.__str__(self)
