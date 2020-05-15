# -*- coding: utf-8 -*-
from cms.api import add_plugin
from haystack.constants import DEFAULT_ALIAS
from haystack.query import SearchQuerySet

from djangocms_blog.models import Post

from .base import BaseTest


class BlogIndexingTests(BaseTest):
    sample_text = ('First post first line This is the description keyword1  '
                   'keyword2 category 1 a tag test body')

    def setUp(self):
        self.get_pages()

    def test_blog_post_is_indexed_using_prepare(self):
        """This tests the indexing path way used by update_index mgmt command"""
        post = self._get_post(self._post_data[0]['en'])
        post = self._get_post(self._post_data[0]['it'], post, 'it')
        post.tags.add('a tag')
        add_plugin(post.content, 'TextPlugin', language='en', body='test body')

        index = self.get_post_index()
        index.index_queryset(DEFAULT_ALIAS)  # initialises index._backend_alias
        indexed = index.prepare(post)

        self.assertEqual(post.get_title(), indexed['title'])
        self.assertEqual(post.get_description(), indexed['description'])
        self.assertEqual(post.get_tags(), indexed['tags'])
        self.assertEqual(self.sample_text, indexed['text'])
        self.assertEqual(post.get_absolute_url(), indexed['url'])
        self.assertEqual(post.date_published, indexed['pub_date'])

    def test_searchqueryset(self):
        posts = self.get_posts()
        all_results = SearchQuerySet().models(Post)
        self.assertEqual(len(posts), len(all_results))
