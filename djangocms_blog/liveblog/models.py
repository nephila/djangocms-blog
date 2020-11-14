from operator import itemgetter

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from cms.models import CMSPlugin
from cms.utils.plugins import reorder_plugins
from django.db import models
from django.template import Context
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from djangocms_text_ckeditor.models import AbstractText
from filer.fields.image import FilerImageField

from djangocms_blog.models import Post, thumbnail_model
from djangocms_blog.settings import DATE_FORMAT


class LiveblogInterface(models.Model):
    """
    Abstract Liveblog plugin model, reusable to customize the liveblogging
    plugins.

    When implementing this, you **must** call ``self._post_save()`` in the
    concrete plugin model ``save`` method.
    """

    publish = models.BooleanField(_("publish liveblog entry"), default=False)
    post_date = models.DateTimeField(_("post date"), blank=True, default=now)

    class Meta:
        verbose_name = _("liveblog entry")
        verbose_name_plural = _("liveblog entries")
        abstract = True

    def __str__(self):
        return str(self.pk)

    def _post_save(self):
        """
        Reorder plugins according to the post_date value. All (and only)
        subclasses of LiveblogInterface are taken into consideration and
        reordered together
        """
        items = []
        for model in LiveblogInterface.__subclasses__():
            items.extend(model.objects.filter(placeholder=self.placeholder).values("pk", "post_date"))
        order = reversed([item["pk"] for item in sorted(items, key=itemgetter("post_date"))])
        reorder_plugins(self.placeholder, None, self.language, order)

    @property
    def liveblog_group(self):
        post = Post.objects.language(self.language).filter(liveblog=self.placeholder).first()
        if post:
            return post.liveblog_group

    def render(self, request):
        context = Context({"request": request})
        from cms.plugin_rendering import ContentRenderer

        renderer = ContentRenderer(request)
        return renderer.render_plugin(
            instance=self,
            context=context,
            placeholder=self.placeholder,
        )

    def send(self, request):
        """
        Render the content and send to the related group
        """
        if self.liveblog_group:
            content = self.render(request)
            notification = {
                "id": self.pk,
                "content": content,
                "creation_date": self.post_date.strftime(DATE_FORMAT),
                "changed_date": self.changed_date.strftime(DATE_FORMAT),
                "type": "send.json",
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(self.liveblog_group, notification)


class Liveblog(LiveblogInterface, AbstractText):
    """
    Basic liveblog plugin model
    """

    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name="%(app_label)s_%(class)s", primary_key=True, parent_link=True, on_delete=models.CASCADE
    )
    title = models.CharField(_("title"), max_length=255)
    image = FilerImageField(
        verbose_name=_("image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="djangocms_blog_liveblog_image",
    )
    thumbnail = models.ForeignKey(
        thumbnail_model,
        verbose_name=_("thumbnail size"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="djangocms_blog_liveblog_thumbnail",
    )

    class Meta:
        verbose_name = _("liveblog entry")
        verbose_name_plural = _("liveblog entries")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._post_save()

    def __str__(self):
        return AbstractText.__str__(self)
