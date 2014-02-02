# -*- coding: utf-8 -*-
try:
    from collections import Counter
except ImportError:
    from .compat import Counter
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.managers import TranslationManager

from .settings import BLOG_TAGCLOUD_MIN, BLOG_TAGCLOUD_MAX


class TaggedFilterItem(object):

    def tagged(self, other_model=None, queryset=None):
        """
        Restituisce una queryset di elementi del model taggati,
        o con gli stessi tag di un model o un queryset
        """
        tags = self._taglist(other_model, queryset)
        return self.get_query_set().filter(taglist__in=tags)

    def _taglist(self, other_model=None, queryset=None):
        """
        Restituisce una lista di id di tag comuni al model corrente e al model
        o queryset passati come argomento
        """
        from taggit.models import TaggedItem
        filtro = None
        if queryset is not None:
            filtro = set()
            for item in queryset.all():
                filtro.update(item.tags.all())
            filtro = set([tag.id for tag in filtro])
        elif other_model is not None:
            filtro = set(TaggedItem.objects.filter(content_type__model=other_model.__name__.lower()).values_list('tag_id', flat=True))
        tags = set(TaggedItem.objects.filter(content_type__model=self.model.__name__.lower()).values_list('tag_id', flat=True))
        if filtro is not None:
            tags = tags.intersection(filtro)
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
        return queryset.values("slug")

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


class GenericDateTaggedManager(TaggedFilterItem, TranslationManager):
    use_for_related_fields = True
    start_date_field = "date_published"
    end_date_field = "date_published_end"
    publish_field = "publish"

    def published(self, queryset=None):
        queryset = self.published_future(queryset)
        if self.start_date_field:
            return queryset.filter(
                **{"%s__lte" % self.start_date_field: datetime.datetime.now()})
        else:
            return queryset

    def published_future(self, queryset=None):
        if queryset is None:
            queryset = self.get_query_set().all()
        if self.end_date_field:
            qfilter = (
                models.Q(**{"%s__gte" % self.end_date_field: datetime.datetime.now()})
                | models.Q(**{"%s__isnull" % self.end_date_field: True})
            )
            queryset = queryset.filter(qfilter)
        return queryset.filter(**{self.publish_field: True})

    def archived(self, queryset=None):
        if queryset is None:
            queryset = self.get_query_set().all()
        if self.end_date_field:
            qfilter = (
                models.Q(**{"%s__lte" % self.end_date_field: datetime.datetime.now()})
                | models.Q(**{"%s__isnull" % self.end_date_field: False})
            )
            queryset = queryset.filter(qfilter)
        return queryset.filter(**{self.publish_field: True})

    def available(self, queryset=None):
        if queryset is None:
            queryset = self.get_query_set().all()
        return queryset.filter(**{self.publish_field: True})

    def filter_by_language(self, language):
        queryset = self.get_query_set()
        return queryset.filter(models.Q(language__isnull=True) | models.Q(language=language))

    def get_months(self, queryset=None):
        """Get months with aggregatet count (how much posts is in the month). Results are ordered by date."""
        if queryset is None:
            queryset = self.get_query_set()
        dates = queryset.values_list(self.start_date_field, flat=True)
        dates = [(x.year, x.month) for x in dates]
        date_counter = Counter(dates)
        dates = set(dates)
        dates = sorted(dates, reverse=True)
        return [{'date': datetime.date(year=year, month=month, day=1),
                 'count': date_counter[year, month]} for year, month in dates]
