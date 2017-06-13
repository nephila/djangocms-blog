# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os.path

from aldryn_apphooks_config.utils import get_app_instance
from cms.api import add_plugin
from cms.toolbar.items import ModalItem
from cms.utils.apphook_reload import reload_urlconf
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from parler.tests.utils import override_parler_settings
from parler.utils.conf import add_default_language_settings
from parler.utils.context import smart_override, switch_language

from djangocms_blog.feeds import FBInstantArticles, FBInstantFeed, LatestEntriesFeed, TagFeed
from djangocms_blog.models import BLOG_CURRENT_NAMESPACE
from djangocms_blog.settings import get_setting
from djangocms_blog.sitemaps import BlogSitemap
from djangocms_blog.views import (
    AuthorEntriesView, CategoryEntriesView, PostArchiveView, PostDetailView, PostListView,
    TaggedListView,
)

from .base import BaseTest


class ViewTest(BaseTest):

    def test_post_list_view(self):
        posts = self.get_posts()
        pages = self.get_pages()

        request = self.get_request(pages[1], 'en', AnonymousUser())

        with smart_override('en'):
            view_obj = PostListView()
            view_obj.request = request
            view_obj.namespace, view_obj.config = get_app_instance(request)
            self.assertEqual(getattr(request, BLOG_CURRENT_NAMESPACE, None), None)

            self.assertEqual(list(view_obj.get_queryset()), [posts[0]])
            self.assertEqual(getattr(request, BLOG_CURRENT_NAMESPACE), self.app_config_1)

            request = self.get_page_request(pages[1], self.user, lang='en', edit=False)
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.request = request
            view_obj.kwargs = {}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 1)
            self.assertEqual(set(qs), set([posts[0]]))

            request = self.get_page_request(pages[1], self.user, lang='en', edit=True)
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.request = request
            self.assertEqual(set(view_obj.get_queryset()), set([posts[0], posts[1], posts[2]]))

            view_obj.kwargs = {}
            view_obj.args = ()
            view_obj.object_list = view_obj.get_queryset()
            view_obj.paginate_by = 1
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [posts[0]])
            self.assertEqual(context['paginator'].count, 3)
            self.assertEqual(context['post_list'][0].title, 'First post')
            response = view_obj.render_to_response(context)
            self.assertContains(response, context['post_list'][0].get_absolute_url())
            self.assertEqual(getattr(request, BLOG_CURRENT_NAMESPACE), self.app_config_1)

            posts[1].sites.add(self.site_2)
            self.assertTrue(view_obj.get_queryset().count(), 2)
            self.assertFalse(posts[1] in view_obj.get_queryset())

        with smart_override('it'):
            request = self.get_page_request(pages[1], self.user, lang='it', edit=True)
            view_obj = PostListView()
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.request = request
            view_obj.args = ()
            view_obj.kwargs = {}
            view_obj.object_list = view_obj.get_queryset()
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertEqual(context['post_list'][0].title, 'Primo post')
            response = view_obj.render_to_response(context)
            self.assertContains(response, context['post_list'][0].get_absolute_url())
            blog_menu = request.toolbar.get_or_create_menu('djangocms_blog', _('Blog'))

            self.assertEqual(len(blog_menu.items), 3)
            self.assertEqual(len(blog_menu.find_items(
                ModalItem, url=reverse('admin:djangocms_blog_post_changelist')
            )), 1)
            self.assertEqual(len(blog_menu.find_items(
                ModalItem, url=reverse('admin:djangocms_blog_post_add')
            )), 1)
            self.assertEqual(len(blog_menu.find_items(
                ModalItem, url=reverse(
                    'admin:djangocms_blog_blogconfig_change', args=(self.app_config_1.pk,)
                )
            )), 1)

    def test_get_view_url(self):
        posts = self.get_posts()
        pages = self.get_pages()

        # Test the custom version of get_view_url against the different namespaces
        request = self.get_request(pages[1], 'en', AnonymousUser())
        view_obj_1 = PostListView()
        view_obj_1.request = request
        view_obj_1.args = ()
        view_obj_1.kwargs = {}
        view_obj_1.namespace, view_obj_1.config = get_app_instance(request)
        self.assertEqual(
            view_obj_1.get_view_url(),
            'http://testserver{0}'.format(pages[1].get_absolute_url())
        )

        request = self.get_request(pages[2], 'en', AnonymousUser())
        view_obj_2 = PostListView()
        view_obj_2.request = request
        view_obj_2.args = ()
        view_obj_2.kwargs = {}
        view_obj_2.namespace, view_obj_2.config = get_app_instance(request)
        self.assertEqual(
            view_obj_2.get_view_url(),
            'http://testserver{0}'.format(pages[2].get_absolute_url())
        )

        view_obj_2.view_url_name = None
        with self.assertRaises(ImproperlyConfigured):
            view_obj_2.get_view_url()

    def test_post_list_view_fallback(self):
        posts = self.get_posts()
        pages = self.get_pages()

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
            request = self.get_page_request(pages[1], self.user, lang='fr', edit=True)
            view_obj.request = request
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.kwargs = {}
            view_obj.object_list = view_obj.get_queryset()
            view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertEqual(view_obj.get_queryset().count(), 3)

            PARLER_FALLBACK = add_default_language_settings(PARLER_FALLBACK)
            with override_parler_settings(PARLER_LANGUAGES=PARLER_FALLBACK):

                view_obj = PostListView()
                request = self.get_page_request(pages[1], self.user, lang='fr', edit=True)
                view_obj.request = request
                view_obj.namespace, view_obj.config = get_app_instance(request)
                view_obj.kwargs = {}
                view_obj.object_list = view_obj.get_queryset()
                view_obj.get_context_data(object_list=view_obj.object_list)
                self.assertEqual(view_obj.get_queryset().count(), 0)

    def test_post_detail_view(self):
        posts = self.get_posts()
        pages = self.get_pages()

        with smart_override('en'):
            with switch_language(posts[0], 'en'):
                request = self.get_page_request(pages[1], AnonymousUser(), lang='en', edit=False)
                view_obj = PostDetailView()
                view_obj.request = request
                view_obj.namespace, view_obj.config = get_app_instance(request)

                with self.assertRaises(Http404):
                    view_obj.kwargs = {'slug': 'not-existing'}
                    post_obj = view_obj.get_object()

                view_obj.kwargs = {'slug': posts[0].slug}
                post_obj = view_obj.get_object()
                self.assertEqual(post_obj, posts[0])
                self.assertEqual(post_obj.language_code, 'en')

        with smart_override('it'):
            with switch_language(posts[0], 'it'):
                request = self.get_page_request(pages[1], AnonymousUser(), lang='it', edit=False)
                view_obj = PostDetailView()
                view_obj.request = request
                view_obj.namespace, view_obj.config = get_app_instance(request)

                view_obj.kwargs = {'slug': posts[0].slug}
                post_obj = view_obj.get_object()
                self.assertEqual(post_obj, posts[0])
                self.assertEqual(post_obj.language_code, 'it')

                view_obj.object = post_obj
                context = view_obj.get_context_data()
                self.assertEqual(context['post'], posts[0])
                self.assertEqual(context['post'].language_code, 'it')
                self.assertTrue(context['meta'])

    def test_post_archive_view(self):
        posts = self.get_posts()
        pages = self.get_pages()

        with smart_override('en'):
            request = self.get_page_request(pages[1], AnonymousUser(), lang='en', edit=False)
            view_obj = PostArchiveView()
            view_obj.request = request
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.kwargs = {'year': now().year, 'month': now().month}

            # One post only, anonymous request
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 1)
            self.assertEqual(list(qs), [posts[0]])

            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertEqual(context['archive_date'].date(), now().replace(year=now().year, month=now().month, day=1).date())

    def test_category_entries_view(self):
        posts = self.get_posts()
        pages = self.get_pages()

        with smart_override('en'):
            request = self.get_page_request(pages[1], self.user, lang='en', edit=True)
            view_obj = CategoryEntriesView()
            view_obj.request = request
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.kwargs = {'category': 'category-1'}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 3)
            self.assertEqual(set(qs), set([posts[0], posts[1], posts[2]]))

            view_obj.paginate_by = 1
            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['category'])
            self.assertEqual(context['category'], self.category_1)
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [posts[0]])
            self.assertEqual(context['paginator'].count, 3)
            self.assertEqual(context['post_list'][0].title, 'First post')

            request = self.get_page_request(pages[1], self.user, edit=False)
            view_obj.request = request
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 1)

    def test_author_entries_view(self):
        posts = self.get_posts()
        pages = self.get_pages()

        with smart_override('en'):
            request = self.get_page_request(pages[1], self.user, lang='en', edit=True)
            view_obj = AuthorEntriesView()
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.request = request
            view_obj.kwargs = {'username': self.user.get_username()}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 3)
            self.assertEqual(set(qs), set([posts[0], posts[1], posts[2]]))

            view_obj.paginate_by = 1
            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['author'])
            self.assertEqual(context['author'], self.user)
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [posts[0]])
            self.assertEqual(context['paginator'].count, 3)
            self.assertEqual(context['post_list'][0].title, 'First post')

            request = self.get_page_request(pages[1], self.user, edit=False)
            view_obj.request = request
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 1)

    def test_taggedlist_view(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        posts[0].save()
        posts[1].tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        posts[1].save()

        with smart_override('en'):
            request = self.get_page_request(pages[1], self.user, lang='en', edit=True)
            view_obj = TaggedListView()
            view_obj.request = request
            view_obj.namespace, view_obj.config = get_app_instance(request)
            view_obj.kwargs = {'tag': 'tag-2'}
            qs = view_obj.get_queryset()
            self.assertEqual(qs.count(), 2)
            self.assertEqual(set(qs), set([posts[0], posts[1]]))

            view_obj.paginate_by = 1
            view_obj.object_list = qs
            context = view_obj.get_context_data(object_list=view_obj.object_list)
            self.assertTrue(context['tagged_entries'], 'tag-2')
            self.assertTrue(context['is_paginated'])
            self.assertEqual(list(context['post_list']), [posts[0]])
            self.assertEqual(context['paginator'].count, 2)
            self.assertEqual(context['post_list'][0].title, 'First post')

    def test_feed(self):
        self.user.first_name = 'Admin'
        self.user.last_name = 'User'
        self.user.save()
        posts = self.get_posts()
        pages = self.get_pages()
        posts[0].tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        posts[0].author = self.user
        posts[0].save()
        posts[1].tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        posts[1].save()
        posts[0].set_current_language('en')

        with smart_override('en'):
            with switch_language(posts[0], 'en'):

                request = self.get_page_request(pages[1], self.user, path=posts[0].get_absolute_url())

                feed = LatestEntriesFeed()
                feed.namespace, feed.config = get_app_instance(request)
                self.assertEqual(list(feed.items()), [posts[0]])
                self.reload_urlconf()
                xml = feed(request)
                self.assertContains(xml, posts[0].get_absolute_url())
                self.assertContains(xml, 'Blog articles on example.com')
                self.assertContains(xml, 'Admin User</dc:creator>')

        with smart_override('it'):
            with switch_language(posts[0], 'it'):
                feed = LatestEntriesFeed()
                feed.namespace, feed.config = get_app_instance(request)
                self.assertEqual(list(feed.items()), [posts[0]])
                request = self.get_page_request(pages[1], self.user, path=posts[0].get_absolute_url())
                xml = feed(request)
                self.assertContains(xml, posts[0].get_absolute_url())
                self.assertContains(xml, 'Articoli del blog su example.com')

                feed = TagFeed()
                feed.namespace = self.app_config_1.namespace
                feed.config = self.app_config_1
                self.assertEqual(list(feed.items('tag-2')), [posts[0]])

    def test_instant_articles(self):
        self.user.first_name = 'Admin'
        self.user.last_name = 'User'
        self.user.save()
        posts = self.get_posts()
        pages = self.get_pages()
        posts[0].tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        posts[0].categories.add(self.category_1)
        posts[0].author = self.user
        posts[0].save()
        add_plugin(
            posts[0].content, 'TextPlugin', language='en', body='<h3>Ciao</h3><p></p><p>Ciao</p>'
        )

        with smart_override('en'):
            with switch_language(posts[0], 'en'):
                request = self.get_page_request(
                    pages[1], self.user, path=posts[0].get_absolute_url()
                )

                feed = FBInstantArticles()
                feed.namespace, feed.config = get_app_instance(request)
                self.assertEqual(list(feed.items()), [posts[0]])
                xml = feed(request)
                self.assertContains(xml, '<guid>{0}</guid>'.format(posts[0].guid))
                self.assertContains(xml, 'content:encoded')
                self.assertContains(xml, 'class="op-modified" datetime="{0}"'.format(
                    posts[0].date_modified.strftime(FBInstantFeed.date_format)
                ))
                self.assertContains(xml, '<link rel="canonical" href="{0}"/>'.format(
                    posts[0].get_full_url()
                ))
                # Assert text transformation
                self.assertContains(xml, '<h2>Ciao</h2><p>Ciao</p>')
                self.assertContains(xml, '<a>Admin User</a>')

    def test_sitemap(self):
        posts = self.get_posts()
        self.get_pages()
        posts[0].tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        posts[0].save()
        posts[1].tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        posts[1].publish = True
        posts[1].save()
        posts[0].set_current_language('en')

        sitemap = BlogSitemap()
        self.assertEqual(len(sitemap.items()), 6)
        for item in sitemap.items():
            self.assertEqual(sitemap.lastmod(item).date(), now().date())
            self.assertEqual(
                sitemap.priority(item), get_setting('SITEMAP_PRIORITY_DEFAULT')
            )
            self.assertEqual(
                sitemap.changefreq(item), get_setting('SITEMAP_CHANGEFREQ_DEFAULT')
            )
            with smart_override(item.get_current_language()):
                self.assertEqual(
                    sitemap.location(item), item.get_absolute_url()
                )

    def test_sitemap_with_unpublished(self):
        posts = self.get_posts()
        pages = self.get_pages()
        sitemap = BlogSitemap()

        self.assertEqual(len(sitemap.items()), 4)

        # unpublish all the pages
        for page in pages:
            page.unpublish('en')
            page.unpublish('it')

        reload_urlconf()

        self.assertEqual(len(sitemap.items()), 0)

    def test_sitemap_config(self):
        posts = self.get_posts()
        self.app_config_1.app_data.config.sitemap_changefreq = 'daily'
        self.app_config_1.app_data.config.sitemap_priority = '0.2'
        self.app_config_1.save()

        sitemap = BlogSitemap()
        self.assertEqual(len(sitemap.items()), 4)
        for item in sitemap.items():
            self.assertEqual(sitemap.lastmod(item).date(), now().date())
            if item.app_config == self.app_config_1:
                self.assertEqual(
                    sitemap.priority(item), '0.2'
                )
                self.assertEqual(
                    sitemap.changefreq(item), 'daily'
                )
            else:
                self.assertEqual(
                    sitemap.priority(item), get_setting('SITEMAP_PRIORITY_DEFAULT')
                )
                self.assertEqual(
                    sitemap.changefreq(item), get_setting('SITEMAP_CHANGEFREQ_DEFAULT')
                )
        self.assertEqual(
            sitemap.priority(None), get_setting('SITEMAP_PRIORITY_DEFAULT')
        )
        self.assertEqual(
            sitemap.changefreq(None), get_setting('SITEMAP_CHANGEFREQ_DEFAULT')
        )

    def test_templates(self):
        posts = self.get_posts()
        pages = self.get_pages()

        with smart_override('en'):
            request = self.get_page_request(pages[1], self.user, edit=True)
            view_obj = PostListView()
            view_obj.request = request
            view_obj.namespace = self.app_config_1.namespace
            view_obj.config = self.app_config_1
            self.assertEqual(view_obj.get_template_names(), os.path.join('djangocms_blog', 'post_list.html'))

            self.app_config_1.app_data.config.template_prefix = 'whatever'
            self.app_config_1.save()
            self.assertEqual(view_obj.get_template_names(), os.path.join('whatever', 'post_list.html'))
            self.app_config_1.app_data.config.template_prefix = ''
            self.app_config_1.save()
