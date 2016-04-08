# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import django
from aldryn_apphooks_config.managers.parler import (
    AppHookConfigTranslatableManager, AppHookConfigTranslatableQueryset,
)
from django.contrib.sites.models import Site
from django.db import models
from django.utils.timezone import now

try:
    from collections import Counter
except ImportError:
    from .compat import Counter


class TaggedFilterItem(object):

    def tagged(self, other_model=None, queryset=None):
        """
        Restituisce una queryset di elementi del model taggati,
        o con gli stessi tag di un model o un queryset
        """
        tags = self._taglist(other_model, queryset)
        return self.get_queryset().filter(tags__in=tags).distinct()

    def _taglist(self, other_model=None, queryset=None):
        """
        Restituisce una lista di id di tag comuni al model corrente e al model
        o queryset passati come argomento
        """
        from taggit.models import TaggedItem
        filter = None
        if queryset is not None:
            filter = set()
            for item in queryset.all():
                filter.update(item.tags.all())
            filter = set([tag.id for tag in filter])
        elif other_model is not None:
            filter = set(TaggedItem.objects.filter(
                content_type__model=other_model.__name__.lower()
            ).values_list('tag_id', flat=True))
        tags = set(TaggedItem.objects.filter(
            content_type__model=self.model.__name__.lower()
        ).values_list('tag_id', flat=True))
        if filter is not None:
            tags = tags.intersection(filter)
        return list(tags)

    def tag_list(self, other_model=None, queryset=None):
        """
        Restituisce un queryset di tag comuni al model corrente e
        al model o queryset passati come argomento
        """
        from taggit.models import Tag
        return Tag.objects.filter(id__in=self._taglist(other_model, queryset))

    def tag_list_slug(self, other_model=None, queryset=None):
        queryset = self.tag_list(other_model, queryset)
        return queryset.values('slug')

    def tag_cloud(self, other_model=None, queryset=None, published=True):
        from taggit.models import TaggedItem
        tag_ids = self._taglist(other_model, queryset)
        kwargs = {}
        if published:
            kwargs = TaggedItem.bulk_lookup_kwargs(self.model.objects.published())
        kwargs['tag_id__in'] = tag_ids
        counted_tags = dict(TaggedItem.objects
                                      .filter(**kwargs)
                                      .values('tag')
                                      .annotate(count=models.Count('tag'))
                                      .values_list('tag', 'count'))
        tags = TaggedItem.tag_model().objects.filter(pk__in=counted_tags.keys())
        for tag in tags:
            tag.count = counted_tags[tag.pk]
        return sorted(tags, key=lambda x: -x.count)


class GenericDateQuerySet(AppHookConfigTranslatableQueryset):
    start_date_field = 'date_published'
    fallback_date_field = 'date_modified'
    end_date_field = 'date_published_end'
    publish_field = 'publish'

    def on_site(self):
        return self.filter(models.Q(sites__isnull=True) |
                           models.Q(sites=Site.objects.get_current().pk))

    def published(self):
        queryset = self.published_future()
        if self.start_date_field:
            return queryset.filter(
                **{'%s__lte' % self.start_date_field: now()})
        else:
            return queryset

    def published_future(self):
        queryset = self.on_site()
        if self.end_date_field:
            qfilter = (
                models.Q(**{'%s__gte' % self.end_date_field: now()}) |
                models.Q(**{'%s__isnull' % self.end_date_field: True})
            )
            queryset = queryset.filter(qfilter)
        return queryset.filter(**{self.publish_field: True})

    def archived(self):
        queryset = self.on_site()
        if self.end_date_field:
            qfilter = (
                models.Q(**{'%s__lte' % self.end_date_field: now()}) |
                models.Q(**{'%s__isnull' % self.end_date_field: False})
            )
            queryset = queryset.filter(qfilter)
        return queryset.filter(**{self.publish_field: True})

    def available(self):
        return self.on_site().filter(**{self.publish_field: True})

    def filter_by_language(self, language):
        return self.active_translations(language_code=language).on_site()


class GenericDateTaggedManager(TaggedFilterItem, AppHookConfigTranslatableManager):
    use_for_related_fields = True

    queryset_class = GenericDateQuerySet

    def get_queryset(self, *args, **kwargs):
        try:
            return super(GenericDateTaggedManager, self).get_queryset(*args, **kwargs)
        except AttributeError:  # pragma: no cover
            return super(GenericDateTaggedManager, self).get_query_set(*args, **kwargs)
    if django.VERSION < (1, 8):
        get_query_set = get_queryset

    def published(self):
        return self.get_queryset().published()

    def available(self):
        return self.get_queryset().available()

    def archived(self):
        return self.get_queryset().archived()

    def published_future(self):
        return self.get_queryset().published_future()

    def filter_by_language(self, language):
        return self.get_queryset().filter_by_language(language)

    def get_months(self, queryset=None):
        """
        Get months with aggregate count (how much posts is in the month).
        Results are ordered by date.
        """
        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.on_site()
        dates_qs = queryset.values_list(queryset.start_date_field, queryset.fallback_date_field)
        dates = []
        for blog_dates in dates_qs:
            if blog_dates[0]:
                current_date = blog_dates[0]
            else:
                current_date = blog_dates[1]
            dates.append((current_date.year, current_date.month,))
        date_counter = Counter(dates)
        dates = set(dates)
        dates = sorted(dates, reverse=True)
        return [{'date': now().replace(year=year, month=month, day=1),
                 'count': date_counter[year, month]} for year, month in dates]
