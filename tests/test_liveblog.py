from datetime import timedelta

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from cms.api import add_plugin
from django.test import RequestFactory
from django.utils.lorem_ipsum import words
from django.utils.timezone import now

from djangocms_blog.cms_appconfig import BlogConfig
from djangocms_blog.liveblog.models import Liveblog
from djangocms_blog.models import Post
from djangocms_blog.settings import DATE_FORMAT

from .base import BaseTest
from .test_utils.routing import application


async def _connect(post):
    path = "liveblog/{namespace}/{lang}/{slug}/".format(
        namespace=post.app_config.namespace,
        lang=post.get_current_language(),
        slug=post.slug,
    )
    communicator = WebsocketCommunicator(application, path)
    connected, __ = await communicator.connect()
    assert connected
    assert await communicator.receive_nothing() is True
    return communicator


def get_request(path="/"):
    factory = RequestFactory()
    request = factory.get(path)
    return request


@database_sync_to_async
def get_post():
    config, __ = BlogConfig.objects.get_or_create(namespace="bla_bla_bla")

    post_data = {"title": words(count=3, common=False), "app_config": config}
    post = Post.objects.create(**post_data)
    post.enable_liveblog = True
    post.save()
    return post


@database_sync_to_async
def delete_post(post):
    post.app_config.delete()
    post.delete()


@database_sync_to_async
def add_livelobg_plugin(placeholder, publish=True):
    plugin_text = words(count=3, common=False)
    plugin = add_plugin(placeholder, "LiveblogPlugin", language="en", body=plugin_text, publish=publish)
    __, admin = plugin.get_plugin_instance()
    admin.save_model(get_request("/"), plugin, None, None)
    return plugin, admin, plugin_text


@database_sync_to_async
def update_livelobg_plugin_content(plugin, publish=True):
    plugin_text = words(count=3, common=False)
    plugin.body = plugin_text
    plugin.publish = publish
    plugin.save()
    __, admin = plugin.get_plugin_instance()
    admin.save_model(get_request("/"), plugin, None, None)
    return plugin, admin, plugin_text


@pytest.mark.debug
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_add_plugin():
    post = await get_post()
    communicator = await _connect(post)
    plugin, admin, plugin_text = await add_livelobg_plugin(post.liveblog)
    rendered = await communicator.receive_json_from()

    assert plugin.pk == rendered["id"]
    assert plugin.creation_date.strftime(DATE_FORMAT) == rendered["creation_date"]
    assert plugin.changed_date.strftime(DATE_FORMAT) == rendered["changed_date"]
    assert rendered["content"].find('data-post-id="{}"'.format(plugin.pk)) > -1
    assert rendered["content"].find(plugin_text) > -1

    plugin, admin, new_plugin_text = await update_livelobg_plugin_content(plugin)
    rendered = await communicator.receive_json_from()

    assert plugin.pk == rendered["id"]
    assert plugin.creation_date.strftime(DATE_FORMAT) == rendered["creation_date"]
    assert plugin.changed_date.strftime(DATE_FORMAT) == rendered["changed_date"]
    assert rendered["content"].find('data-post-id="{}"'.format(plugin.pk)) > -1
    assert rendered["content"].find(new_plugin_text) > -1
    assert rendered["content"].find(plugin_text) == -1

    await communicator.disconnect()
    await delete_post(post)


@pytest.mark.skip
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_add_plugin_no_publish():
    post = await get_post()
    communicator = await _connect(post)
    plugin, admin, plugin_text = await add_livelobg_plugin(post.liveblog, publish=False)
    assert await communicator.receive_nothing() is True
    await communicator.send_json_to({"hello": "world"})
    rendered = await communicator.receive_json_from()

    plugin, admin, new_plugin_text = await update_livelobg_plugin_content(plugin, publish=True)
    rendered = await communicator.receive_json_from()

    assert plugin.pk == rendered["id"]
    assert plugin.creation_date.strftime(DATE_FORMAT) == rendered["creation_date"]
    assert plugin.changed_date.strftime(DATE_FORMAT) == rendered["changed_date"]
    assert rendered["content"].find('data-post-id="{}"'.format(plugin.pk)) > -1
    assert rendered["content"].find(new_plugin_text) > -1
    assert rendered["content"].find(plugin_text) == -1

    await communicator.disconnect()
    await delete_post(post)


@pytest.mark.skip
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_disconnect():
    post = await get_post()
    communicator = await _connect(post)

    plugin, admin, plugin_text = await add_livelobg_plugin(post.liveblog)
    rendered = await communicator.receive_json_from()
    assert rendered["content"]

    await communicator.disconnect()

    await update_livelobg_plugin_content(plugin)

    assert await communicator.receive_nothing() is True
    await delete_post(post)


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_nopost():
    post = await get_post()
    post.slug = "something"
    communicator = await _connect(post)

    assert await communicator.receive_nothing() is True
    await communicator.disconnect()
    await delete_post(post)


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_plugin_not_liveblog_placeholder():
    @database_sync_to_async
    def get_group(plugin):
        return plugin.liveblog_group

    post = await get_post()
    communicator = await _connect(post)

    plugin, _admin, _plugin_text = await add_livelobg_plugin(post.content)
    liveblog_group = await get_group(plugin)
    assert liveblog_group is None
    assert await communicator.receive_nothing() is True
    await communicator.disconnect()
    await delete_post(post)


class LiveBlogTest(BaseTest):
    def setUp(self):
        Liveblog.objects.all().delete()
        super().setUp()

    def test_plugin_render(self):
        pages = self.get_pages()
        posts = self.get_posts()
        post = posts[0]
        post.enable_liveblog = True
        post.save()
        plugin = add_plugin(post.liveblog, "LiveblogPlugin", language="en", body="live text", publish=False)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=False)
        self.assertFalse(rendered.strip())

        plugin.publish = True
        plugin.save()
        rendered = self.render_plugin(pages[0], "en", plugin, edit=False)
        self.assertTrue(rendered.find('data-post-id="{}"'.format(plugin.pk)) > -1)
        self.assertTrue(rendered.find("live text") > -1)

    def test_plugins_order(self):
        self.get_pages()
        posts = self.get_posts()
        post = posts[0]
        post.enable_liveblog = True
        post.save()

        current_date = now()

        plugin_1 = add_plugin(
            post.liveblog,
            "LiveblogPlugin",
            language="en",
            body="plugin 1",
            publish=True,
            post_date=current_date - timedelta(seconds=1),
        )
        plugin_2 = add_plugin(
            post.liveblog,
            "LiveblogPlugin",
            language="en",
            body="plugin 2",
            publish=True,
            post_date=current_date - timedelta(seconds=5),
        )
        plugin_3 = add_plugin(
            post.liveblog,
            "LiveblogPlugin",
            language="en",
            body="plugin 3",
            publish=True,
            post_date=current_date - timedelta(seconds=10),
        )
        self.assertEqual(
            list(Liveblog.objects.all().order_by("position").values_list("pk", flat=True)),
            [plugin_1.pk, plugin_2.pk, plugin_3.pk],
        )

        plugin_1.post_date = current_date - timedelta(seconds=20)
        plugin_1.save()
        self.assertEqual(
            list(Liveblog.objects.all().order_by("position").values_list("pk", flat=True)),
            [plugin_2.pk, plugin_3.pk, plugin_1.pk],
        )
