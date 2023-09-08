from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    sites = models.ManyToManyField("sites.Site")

    def get_sites(self):
        return self.sites


from cms.models import PlaceholderRelationField  # noqa isort:skip
from djangocms_blog.models import Post  # noqa isort:skip


class PostExtension(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="extension")
    some_field = models.CharField(max_length=10)


class PostPlaceholderExtension(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="placeholder")
    some_placeholder = PlaceholderRelationField("some_placeholder", related_name="some_placeholder")

    def delete(self):
        super().delete()
