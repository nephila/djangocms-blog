import os
from unittest.mock import MagicMock, patch

from cms.api import add_plugin

from djangocms_blog.templatetags.djangocms_blog import media_images, media_plugins

from .base import BaseTest


class MediaTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.get_pages()
        posts = self.get_posts()
        self.post = posts[0]
        self.youtube = add_plugin(
            self.post.media, "YouTubePlugin", language="en", url="https://www.youtube.com/watch?v=szbGc7ymFhQ"
        )
        self.vimeo = add_plugin(self.post.media, "VimeoPlugin", language="en", url="https://vimeo.com/12915013")
        self.media_text = add_plugin(self.post.media, "TextPlugin", language="en", body="random text")
        self.general_text = add_plugin(self.post.content, "TextPlugin", language="en", body="body text")

    def _get_request_mock(self, json_path):
        response = self.read_json(json_path)
        response_mock = MagicMock()
        response_mock.json.return_value = response
        return response_mock

    def test_no_media_plugins(self):
        self.post.media.get_plugins().delete()
        context = {"request": self.request("/")}
        plugins = media_plugins(context, self.post)
        self.assertEqual(0, len(plugins))

    def test_media_plugins(self):
        context = {"request": self.request("/")}
        plugins = media_plugins(context, self.post)
        self.assertEqual(3, len(plugins))
        self.assertIn(self.youtube, plugins)
        self.assertIn(self.vimeo, plugins)
        self.assertIn(self.media_text, plugins)
        self.assertNotIn(self.general_text, plugins)

    @patch("tests.media_app.models.Vimeo.vimeo_data")
    def test_djangocms_video_plugins(self, vimeo_data):
        vimeo_data.return_value = {
            "main_url": "https://i.vimeocdn.com/video/73266401_200x150.jpg",
            "thumb_url": "https://i.vimeocdn.com/video/73266401_200x150.jpg",
        }
        filer_image = self.create_filer_image_object()
        src_thumbs = [
            "https://img.youtube.com/vi/szbGc7ymFhQ/hqdefault.jpg",
            "https://i.vimeocdn.com/video/73266401_200x150.jpg",
            filer_image.url,
        ]
        add_plugin(self.post.media, "VideoPlayerPlugin", language="en", poster=filer_image)
        context = {"request": self.request("/")}
        images = media_images(context, self.post, main=False)
        self.assertEqual(3, len(images))
        self.assertEqual(images, src_thumbs)

    @patch("tests.media_app.models.requests.get")
    def test_media_images(self, get_request):
        src_images = [
            "https://img.youtube.com/vi/szbGc7ymFhQ/maxresdefault.jpg",
            "https://i.vimeocdn.com/video/73266401_640.jpg",
        ]
        src_thumbs = [
            "https://img.youtube.com/vi/szbGc7ymFhQ/hqdefault.jpg",
            "https://i.vimeocdn.com/video/73266401_200x150.jpg",
        ]
        get_request.return_value = self._get_request_mock(os.path.join("fixtures", "vimeo.json"))
        context = {"request": self.request("/")}
        images = media_images(context, self.post)
        self.assertEqual(2, len(images))
        self.assertEqual(images, src_images)

        images = media_images(context, self.post, main=False)
        self.assertEqual(2, len(images))
        self.assertEqual(images, src_thumbs)

    @patch("tests.media_app.models.requests.get")
    def test_media_attributes(self, get_request):
        src_ids = ["szbGc7ymFhQ", "12915013"]
        get_request.return_value = self._get_request_mock(os.path.join("fixtures", "vimeo.json"))
        context = {"request": self.request("/")}
        plugins = media_plugins(context, self.post)
        dst_ids = [media.media_id for media in plugins if hasattr(media, "media_id")]
        self.assertEqual(dst_ids, src_ids)
