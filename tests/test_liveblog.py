# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json
from unittest import SkipTest

try:
    from channels import Channel
    from channels.tests import ChannelTestCase
    from cms.api import add_plugin

    from djangocms_blog.liveblog.consumers import liveblog_connect, liveblog_disconnect
    from djangocms_blog.liveblog.models import DATE_FORMAT
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
            posts = self.get_posts()
            self.get_pages()
            post = posts[0]
            post.enable_liveblog = True
            post.save()

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', post.slug)

            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='live text', publish=True
            )
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
            posts = self.get_posts()
            self.get_pages()
            post = posts[0]
            post.enable_liveblog = True
            post.save()

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', post.slug)

            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='live text', publish=False
            )
            result = self.get_next_message(message.reply_channel.name, require=False)
            self.assertIsNone(result)

            plugin.publish = True
            plugin.save()

            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])

            rendered = json.loads(result['text'])
            self.assertEqual(plugin.pk, rendered['id'])
            self.assertEqual(plugin.creation_date.strftime(DATE_FORMAT), rendered['creation_date'])
            self.assertEqual(plugin.changed_date.strftime(DATE_FORMAT), rendered['changed_date'])
            self.assertTrue(rendered['content'].find('data-post-id="{}"'.format(plugin.pk)) > -1)
            self.assertTrue(rendered['content'].find('live text') > -1)

        def test_disconnect(self):
            posts = self.get_posts()
            self.get_pages()
            post = posts[0]
            post.enable_liveblog = True
            post.save()

            Channel('setup').send({'connect': 1, 'reply_channel': 'reply'})
            message = self.get_next_message('setup', require=True)
            liveblog_connect(message, self.app_config_1.namespace, 'en', post.slug)

            plugin = add_plugin(
                post.liveblog, 'LiveblogPlugin', language='en', body='live text', publish=True
            )
            result = self.get_next_message(message.reply_channel.name, require=True)
            self.assertTrue(result['text'])

            liveblog_disconnect(message, self.app_config_1.namespace, 'en', post.slug)

            plugin.body = 'modified text'
            plugin.save()

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
            context = self.get_plugin_context(pages[0], 'en', plugin, edit=False)
            rendered = plugin.render_plugin(context, post.liveblog)
            self.assertFalse(rendered.strip())

            plugin.publish = True
            plugin.save()
            context = self.get_plugin_context(pages[0], 'en', plugin, edit=False)
            rendered = plugin.render_plugin(context, post.liveblog)
            self.assertTrue(rendered.find('data-post-id="{}"'.format(plugin.pk)) > -1)
            self.assertTrue(rendered.find('live text') > -1)

except ImportError:  # pragma: no cover
    pass
