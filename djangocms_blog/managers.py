# -*- coding: utf-8 -*-
from collections import Counter
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from hvad.manager import TranslationManager

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
        qs = self.tag_list(other_model, queryset)
        return qs.values("slug")

    def tag_cloud(self, other_model=None, queryset=None, start=None):
        from taggit_templatetags.templatetags.taggit_extras import get_weight_fun
        from taggit.models import TaggedItem
        tag_ids = self._taglist(other_model, queryset)
        tagquery = TaggedItem.tags_for(self.model).filter(id__in=tag_ids)
        if start is not None:
            tagquery = tagquery.filter(name__istartswith=start)
        tagquery = tagquery.annotate(count=models.Count('taggit_taggeditem_items'))
        count = tagquery.values_list('count', flat=True)
        if len(count) > 0:
            weight_fun = get_weight_fun(BLOG_TAGCLOUD_MIN,
                                        BLOG_TAGCLOUD_MAX,
                                        min(count), max(count))
            tagquery = tagquery.order_by('name')
            for tag in tagquery:
                tag.weight = weight_fun(tag.count)
        return tagquery


class GenericDateTaggedManager(TaggedFilterItem, TranslationManager):
    use_for_related_fields = True
    start_date_field = "date_published"
    end_date_field = "date_published_end"
    publish_field = "publish"

    def published(self, qs=None):
        qs = self.published_future(qs)
        if self.start_date_field:
            return qs.filter(
                **{"%s__lte" % self.start_date_field: datetime.datetime.now()})
        else:
            return qs

    def published_future(self, qs=None):
        if not qs:
            qs = self.get_query_set().all()
        if self.end_date_field:
            qfilter = (
                models.Q(**{"%s__gte" % self.end_date_field: datetime.datetime.now()})
                | models.Q(**{"%s__isnull" % self.end_date_field: True})
            )
            qs = qs.filter(qfilter)
        return qs.filter(**{self.publish_field: True})

    def archived(self, qs=None):
        if not qs:
            qs = self.get_query_set().all()
        if self.end_date_field:
            qfilter = (
                models.Q(**{"%s__lte" % self.end_date_field: datetime.datetime.now()})
                | models.Q(**{"%s__isnull" % self.end_date_field: False})
            )
            qs = qs.filter(qfilter)
        return qs.filter(**{self.publish_field: True})

    def available(self, qs=None):
        if not qs:
            qs = self.get_query_set().all()
        return qs.filter(**{self.publish_field: True})

    def filter_by_language(self, language):
        qs = self.get_query_set()
        return qs.filter(models.Q(language__isnull=True) | models.Q(language=language))

    def get_months(self, queryset=None):
        """Get months with aggregatet count (how much posts is in the month). Results are ordered by date."""
        # done via naive way as django's having tough time while aggregating on date fields
        if not queryset:
            queryset = self.get_query_set()
        dates = queryset.values_list(self.start_date_field, flat=True)
        dates = [(x.year, x.month) for x in dates]
        date_counter = Counter(dates)
        dates = set(dates)
        dates = sorted(dates, reverse=True)
        return [{'date': datetime.date(year=year, month=month, day=1),
                 'count': date_counter[year, month]} for year, month in dates]
