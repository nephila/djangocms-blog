# -*- coding: utf-8 -*-
from datetime import date
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.utils.translation import activate
from djangocms_blog.views import PostListView, PostDetailView, PostArchiveView

from . import BaseTest


class ViewTest(BaseTest):

    def test_post_list_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        request = self.get_page_request(page1, AnonymousUser(), r'/en/blog/', edit=False)
        activate('en')
        view_obj = PostListView()
        view_obj.request = request

        self.assertEqual(list(view_obj.get_queryset()), [post1])

        request = self.get_page_request(page1, self.user, r'/en/blog/', edit=False)
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

        request = self.get_page_request(page1, self.user, r'/it/blog/', lang_code='it', edit=False)
        activate('it')
        view_obj.request = request
        view_obj.object_list = view_obj.get_queryset()
        context = view_obj.get_context_data(object_list=view_obj.object_list)
        self.assertEqual(context['post_list'][0].title, 'Secondo post')
        response = view_obj.render_to_response(context)
        self.assertContains(response, context['post_list'][0].get_absolute_url())

    def test_post_detail_view(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()

        request = self.get_page_request(page1, AnonymousUser(), r'/en/blog/', edit=False)
        activate('en')
        view_obj = PostDetailView()
        view_obj.request = request

        with self.assertRaises(Http404):
            view_obj.kwargs = {'slug': 'not-existing'}
            post_obj = view_obj.get_object()

        view_obj.kwargs = {'slug': post1.slug}
        post_obj = view_obj.get_object()
        self.assertEqual(post_obj, post1)
        self.assertEqual(post_obj.language_code, 'en')

        request = self.get_page_request(page1, AnonymousUser(), r'/it/blog/', lang_code='it', edit=False)
        activate('it')
        post1.set_current_language('it')
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

        request = self.get_page_request(page1, AnonymousUser(), r'/en/blog/', edit=False)
        activate('en')
        view_obj = PostArchiveView()
        view_obj.request = request
        view_obj.kwargs = {'year': date.today().year, 'month': date.today().month}

        # One post only, anonymous request
        qs = view_obj.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(list(qs), [post1])

        view_obj.object_list = qs
        context = view_obj.get_context_data(object_list=view_obj.object_list)
        self.assertEqual(context['archive_date'], date(year=date.today().year, month=date.today().month, day=1))
        
    def test_category_entries_views(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()