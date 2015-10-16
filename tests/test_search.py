# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from djangocms_blog.search_indexes import PostIndex
from . import BaseTest

from haystack.constants import DEFAULT_ALIAS


class PluginIndexingTests(BaseTest):

    def setUp(self):
        self.index = PostIndex()

    def test_blog_post_is_indexed_using_prepare(self):
        """This tests the indexing path way used by update_index mgmt command"""
        post = self._get_post(self._post_data[0]['en'])
        post = self._get_post(self._post_data[0]['it'], post, 'it')
        index = self.get_post_index()
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(post)
        print(indexed)
        self.assertEqual(post.get_title(), indexed['title'])
        self.assertEqual(post.get_description(), indexed['description'])
        self.assertEqual('First post First post first line This is the description category 1', indexed['text'])
        self.assertEqual(post.get_absolute_url(), indexed['url'])
        self.assertEqual(post.date_published.strftime("%Y-%m-%d %H:%M:%S"), indexed['pub_date'])

    def test_blog_post_is_indexed_using_update_object(self):
        """This tests the indexing path way used by the RealTimeSignalProcessor"""
        post = self._get_post(self._post_data[0]['en'])
        post = self._get_post(self._post_data[0]['it'], post, 'it')
        index = self.get_post_index()
        index.update_object(post, using=DEFAULT_ALIAS)
        indexed = index.prepared_data
        print(indexed)
        self.assertEqual(post.get_title(), indexed['title'])
        self.assertEqual(post.get_description(), indexed['description'])
        self.assertEqual('First post First post first line This is the description category 1', indexed['text'])
        self.assertEqual(post.get_absolute_url(), indexed['url'])
        self.assertEqual(post.date_published.strftime("%Y-%m-%d %H:%M:%S"), indexed['pub_date'])

