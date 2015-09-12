# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.utils.timezone import now
from parler.tests.utils import override_parler_settings
from parler.utils.conf import add_default_language_settings
from parler.utils.context import smart_override, switch_language

from djangocms_blog.feeds import LatestEntriesFeed, TagFeed
from djangocms_blog.sitemaps import BlogSitemap
from djangocms_blog.views import (
    AuthorEntriesView, CategoryEntriesView, PostArchiveView, PostDetailView, PostListView,
    TaggedListView,
)

from . import BaseTest


class ViewTest(BaseTest):

    def test_post_list_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        request = self.get_page_request(page1, AnonymousUser(), r'/en/blog/', edit=False)

        with smart_override('en'):
            view_obj = PostListView()
            view_obj.request = request

            self.assertEqual(list(view_obj.get_queryset()), [post1])

            request = self.get_page_request(page1, self.user, r'/en/blog/', edit=False)
            view_obj.request = request
            view_obj.kwargs = {}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 1)
            self.assertEqual(set(qs), set([post1]))

            request = self.get_page_request(page1, self.user, r'/en/blog/', edit=True)
            view_obj.request = request
            self.assertEqual(set(view_obj.get_queryset()), set([post1, post2]))

            view_obj.kwargs = {}
            view_obj.object_list = view_obj.get_queryset()
            view_obj.paginate_by = 1
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [post2])
            self.assertEqual(context['paginator'].count, 2)
            self.assertEqual(context['post_list'][0].title, 'Second post')
            response = view_obj.render_to_response(context)
            self.assertContains(response, context['post_list'][0].get_absolute_url())

        with smart_override('it'):
            request = self.get_page_request(page1, self.user, r'/it/blog/', lang='it', edit=True)
            view_obj.request = request
            view_obj.object_list = view_obj.get_queryset()
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertEqual(context['post_list'][0].title, 'Secondo post')
            response = view_obj.render_to_response(context)
            self.assertContains(response, context['post_list'][0].get_absolute_url())

    def test_post_list_view_fallback(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        PARLER_FALLBACK = {
            1: (
                {'code': 'en'},
                {'code': 'it'},
                {'code': 'fr', 'hide_untranslated': True},
            ),
            'default': {
                'fallback': 'en',
                'hide_untranslated': False,
            }
        }

        with smart_override('fr'):
            view_obj = PostListView()
            request = self.get_page_request(page1, self.user, r'/fr/blog/', lang='fr', edit=True)
            view_obj.request = request
            view_obj.kwargs = {}
            view_obj.object_list = view_obj.get_queryset()
            view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertEqual(view_obj.get_queryset().count(), 2)

            PARLER_FALLBACK = add_default_language_settings(PARLER_FALLBACK)
            with override_parler_settings(PARLER_LANGUAGES=PARLER_FALLBACK):

                view_obj = PostListView()
                request = self.get_page_request(page1, self.user, r'/fr/blog/', lang='fr', edit=True)
                view_obj.request = request
                view_obj.kwargs = {}
                view_obj.object_list = view_obj.get_queryset()
                view_obj.get_context_data(object_list=view_obj.object_list)
                self.assertEqual(view_obj.get_queryset().count(), 0)

    def test_post_detail_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        with smart_override('en'):
            with switch_language(post1, 'en'):
                request = self.get_page_request(page1, AnonymousUser(), r'/en/blog/', edit=False)
                view_obj = PostDetailView()
                view_obj.request = request

                with self.assertRaises(Http404):
                    view_obj.kwargs = {'slug': 'not-existing'}
                    post_obj = view_obj.get_object()

                view_obj.kwargs = {'slug': post1.slug}
                post_obj = view_obj.get_object()
                self.assertEqual(post_obj, post1)
                self.assertEqual(post_obj.language_code, 'en')

        with smart_override('it'):
            with switch_language(post1, 'it'):
                request = self.get_page_request(page1, AnonymousUser(), r'/it/blog/', lang='it', edit=False)
                view_obj.request = request
                view_obj.kwargs = {'slug': post1.slug}
                post_obj = view_obj.get_object()
                self.assertEqual(post_obj, post1)
                self.assertEqual(post_obj.language_code, 'it')

                view_obj.object = post_obj
                context = view_obj.get_context_data()
                self.assertEqual(context['post'], post1)
                self.assertEqual(context['post'].language_code, 'it')
                self.assertTrue(context['meta'])

    def test_post_archive_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        with smart_override('en'):
            request = self.get_page_request(page1, AnonymousUser(), r'/en/blog/', edit=False)
            view_obj = PostArchiveView()
            view_obj.request = request
            view_obj.kwargs = {'year': now().year, 'month': now().month}

            # One post only, anonymous request
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 1)
            self.assertEqual(list(qs), [post1])

            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertEqual(context['archive_date'].date(), now().replace(year=now().year, month=now().month, day=1).date())

    def test_category_entries_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        with smart_override('en'):
            request = self.get_page_request(page1, self.user, r'/en/blog/', edit=True)
            view_obj = CategoryEntriesView()
            view_obj.request = request
            view_obj.kwargs = {'category': 'category-1'}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 2)
            self.assertEqual(set(qs), set([post1, post2]))

            view_obj.paginate_by = 1
            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['category'])
            self.assertEqual(context['category'], self.category_1)
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [post2])
            self.assertEqual(context['paginator'].count, 2)
            self.assertEqual(context['post_list'][0].title, 'Second post')

    def test_author_entries_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        with smart_override('en'):
            request = self.get_page_request(page1, self.user, r'/en/blog/', edit=True)
            view_obj = AuthorEntriesView()
            view_obj.request = request
            view_obj.kwargs = {'username': self.user.get_username()}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 2)
            self.assertEqual(set(qs), set([post1, post2]))

            view_obj.paginate_by = 1
            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['author'])
            self.assertEqual(context['author'], self.user)
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [post2])
            self.assertEqual(context['paginator'].count, 2)
            self.assertEqual(context['post_list'][0].title, 'Second post')

    def test_taggedlist_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()
        post1.tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        post1.save()
        post2.tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        post2.save()

        with smart_override('en'):
            request = self.get_page_request(page1, self.user, r'/en/blog/', edit=True)
            view_obj = TaggedListView()
            view_obj.request = request
            view_obj.kwargs = {'tag': 'tag-2'}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 2)
            self.assertEqual(set(qs), set([post1, post2]))

            view_obj.paginate_by = 1
            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['tagged_entries'], 'tag-2')
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [post2])
            self.assertEqual(context['paginator'].count, 2)
            self.assertEqual(context['post_list'][0].title, 'Second post')

    def test_feed(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()
        post1.tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        post1.save()
        post2.tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        post2.save()
        post1.set_current_language('en')

        feed = LatestEntriesFeed()
        self.assertEqual(list(feed.items()), [post1])
        request = self.get_page_request(page1, self.user, r'/en/blog/', lang='en', edit=False)
        xml = feed(request)
        self.assertContains(xml, post1.get_absolute_url())
        self.assertContains(xml, 'Blog articles on example.com')

        with smart_override('it'):
            with switch_language(post1, 'it'):
                feed = LatestEntriesFeed()
                self.assertEqual(list(feed.items()), [post1])
                request = self.get_page_request(page1, self.user, r'/it/blog/', lang='it', edit=False)
                xml = feed(request)
                self.assertContains(xml, post1.get_absolute_url())
                self.assertContains(xml, 'Articoli del blog su example.com')

                feed = TagFeed()
                self.assertEqual(list(feed.items('tag-2')), [post1])

    def test_sitemap(self):
        post1, post2 = self.get_posts()
        post1.tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        post1.save()
        post2.tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        post2.publish = True
        post2.save()
        post1.set_current_language('en')

        sitemap = BlogSitemap()
        self.assertEqual(sitemap.items().count(), 2)
        for item in sitemap.items():
            self.assertTrue(sitemap.lastmod(item).date(), now().today())
