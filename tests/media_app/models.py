import re

import requests
from cms.models import CMSPlugin
from django.db import models

from djangocms_blog.media.base import MediaAttachmentPluginMixin


class YoutTubeVideo(MediaAttachmentPluginMixin, CMSPlugin):
    url = models.URLField("video URL")

    _media_autoconfiguration = {
        "params": [
            re.compile("^https://youtu.be/(?P<media_id>[-\\w]+)$"),
            re.compile("^https://www.youtube.com/watch\\?v=(?P<media_id>[-\\w]+)$"),
        ],
        "thumb_url": "https://img.youtube.com/vi/%(media_id)s/hqdefault.jpg",
        "main_url": "https://img.youtube.com/vi/%(media_id)s/maxresdefault.jpg",
        "callable": None,
    }

    def __str__(self):
        return self.url

    @property
    def media_url(self):
        return self.url


class Vimeo(MediaAttachmentPluginMixin, CMSPlugin):
    url = models.URLField("Video URL")

    _media_autoconfiguration = {
        "params": [re.compile("^https://vimeo.com/(?P<media_id>[-0-9]+)$")],
        "thumb_url": "%(thumb_url)s",
        "main_url": "%(main_url)s",
        "callable": "vimeo_data",
    }

    def __str__(self):
        return self.url

    @property
    def media_url(self):
        return self.url

    @property
    def media_title(self):
        try:
            return self.media_params["title"]
        except KeyError:
            return None

    def vimeo_data(self, media_id):
        response = requests.get(
            "https://vimeo.com/api/v2/video/{media_id}.json".format(
                media_id=media_id,
            )
        )
        json = response.json()
        data = {}
        if json:
            data = json[0]
            data.update(
                {"media_id": media_id, "main_url": data["thumbnail_large"], "thumb_url": data["thumbnail_medium"]}
            )
        return data
