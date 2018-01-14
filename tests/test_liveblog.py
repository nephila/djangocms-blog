# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json
from datetime import timedelta
from unittest import SkipTest

from django.utils.timezone import now

try:
    from channels import Channel
    from channels.tests import ChannelTestCase
    from cms.api import add_plugin

    from djangocms_blog.liveblog.consumers import liveblog_connect, liveblog_disconnect
    from djangocms_blog.liveblog.models import DATE_FORMAT, Liveblog
    from .base import BaseTest


    class LiveBlogTest(BaseTest, ChannelTestCase):

        @classmethod
        def setUpClass(cls):
            try:
                import knocker
                super(LiveBlogTest, cls).setUpClass()
            except ImportError:
                raise SkipTest('channels not installed, skipping tests')

        def test_add_plugin(self):
            pages = self.get_pages()
            posts = self.get_posts()
            post = posts[0]
            post.enable_liveblog = True
            post.save()
            request = self.get_request(pages[0], user=self.user, lang='en')

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', post.slug)
            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['accept'])

            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='live text', publish=True
            )
            __, admin = plugin.get_plugin_instance()
            admin.save_model(request, plugin, None, None)
            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])

            rendered = json.loads(result['text'])
            self.assertEqual(plugin.pk, rendered['id'])
            self.assertEqual(plugin.creation_date.strftime(DATE_FORMAT), rendered['creation_date'])
            self.assertEqual(plugin.changed_date.strftime(DATE_FORMAT), rendered['changed_date'])
            self.assertTrue(rendered['content'].find('data-post-id="{}"'.format(plugin.pk)) > -1)
            self.assertTrue(rendered['content'].find('live text') > -1)

            plugin.body = 'modified text'
            plugin.save()
            admin.save_model(request, plugin, None, None)

            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])

            rendered = json.loads(result['text'])
            self.assertEqual(plugin.pk, rendered['id'])
            self.assertEqual(plugin.creation_date.strftime(DATE_FORMAT), rendered['creation_date'])
            self.assertEqual(plugin.changed_date.strftime(DATE_FORMAT), rendered['changed_date'])
            self.assertTrue(rendered['content'].find('data-post-id="{}"'.format(plugin.pk)) > -1)
            self.assertTrue(rendered['content'].find('modified text') > -1)
            self.assertTrue(rendered['content'].find('live text') == -1)

        def test_add_plugin_no_publish(self):
            pages = self.get_pages()
            posts = self.get_posts()
            post = posts[0]
            post.enable_liveblog = True
            post.save()
            request = self.get_request(pages[0], user=self.user, lang='en')

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', post.slug)
            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['accept'])

            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='live text', publish=False
            )
            __, admin = plugin.get_plugin_instance()
            admin.save_model(request, plugin, None, None)
            result = self.get_next_message(message.reply_channel.name, require=False)
            self.assertIsNone(result)

            plugin.publish = True
            plugin.save()
            admin.save_model(request, plugin, None, None)

            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])

            rendered = json.loads(result['text'])
            self.assertEqual(plugin.pk, rendered['id'])
            self.assertEqual(plugin.creation_date.strftime(DATE_FORMAT), rendered['creation_date'])
            self.assertEqual(plugin.changed_date.strftime(DATE_FORMAT), rendered['changed_date'])
            self.assertTrue(rendered['content'].find('data-post-id="{}"'.format(plugin.pk)) > -1)
            self.assertTrue(rendered['content'].find('live text') > -1)

        def test_disconnect(self):
            pages = self.get_pages()
            posts = self.get_posts()
            post = posts[0]
            post.enable_liveblog = True
            post.save()
            request = self.get_request(pages[0], user=self.user, lang='en')

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', post.slug)
            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['accept'])

            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='live text', publish=True
            )
            __, admin = plugin.get_plugin_instance()
            admin.save_model(request, plugin, None, None)
            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])

            liveblog_disconnect(message, self.app_config_1.namespace, 'en', post.slug)

            plugin.body = 'modified text'
            plugin.save()
            admin.save_model(request, plugin, None, None)

            result = self.get_next_message(message.reply_channel.name, require=False)
            self.assertIsNone(result)

        def test_nopost(self):

            self.get_pages()

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', 'random-post')

            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])
            rendered = json.loads(result['text'])
            self.assertTrue(rendered['error'], 'no_post')

            liveblog_disconnect(message, self.app_config_1.namespace, 'en', 'random-post')
            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])
            rendered = json.loads(result['text'])
            self.assertTrue(rendered['error'], 'no_post')

        def test_plugin_without_post(self):

            pages = self.get_pages()

            placeholder = pages[0].get_placeholders().get(slot='content')

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', 'random post')
            self.get_next_message(message.reply_channel.name, require=True)

            plugin = add_plugin(
                placeholder, 'LiveblogPlugin', language='en', body='live text', publish=True
            )
            self.assertIsNone(plugin.liveblog_group)
            result = self.get_next_message(message.reply_channel.name, require=False)
            self.assertIsNone(result)

        def test_plugin_render(self):
            posts = self.get_posts()
            pages = self.get_pages()
            post = posts[0]
            post.enable_liveblog = True
            post.save()
            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='live text', publish=False
            )
            rendered = self.render_plugin(pages[0], 'en', plugin, edit=True)
            self.assertFalse(rendered.strip())

            plugin.publish = True
            plugin.save()
            rendered = self.render_plugin(pages[0], 'en', plugin, edit=True)
            self.assertTrue(rendered.find('data-post-id="{}"'.format(plugin.pk)) > -1)
            self.assertTrue(rendered.find('live text') > -1)

        def test_plugins_order(self):
            posts = self.get_posts()
            self.get_pages()
            post = posts[0]
            post.enable_liveblog = True
            post.save()

            current_date = now()

            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='plugin 1', publish=True,
                post_date=current_date - timedelta(seconds=1)
            )
            add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='plugin 2', publish=True,
                post_date=current_date - timedelta(seconds=5)
            )
            add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='plugin 3', publish=True,
                post_date=current_date - timedelta(seconds=10)
            )
            self.assertEqual(list(Liveblog.objects.all().order_by('position').values_list('pk', flat=True)), [1, 2, 3])

            plugin.post_date = current_date - timedelta(seconds=20)
            plugin.save()
            self.assertEqual(list(Liveblog.objects.all().order_by('position').values_list('pk', flat=True)), [2, 3, 1])

except ImportError:  # pragma: no cover
    pass
