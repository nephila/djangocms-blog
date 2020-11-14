from collections import Counter

from aldryn_apphooks_config.managers.parler import AppHookConfigTranslatableManager, AppHookConfigTranslatableQueryset
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils.timezone import now


class TaggedFilterItem:
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

        filters = None
        if queryset is not None:
            filters = set()
            for item in queryset.all():
                filters.update(item.tags.all())
            filters = {tag.id for tag in filters}
        elif other_model is not None:
            filters = set(
                TaggedItem.objects.filter(content_type__model=other_model.__name__.lower()).values_list(
                    "tag_id", flat=True
                )
            )
        tags = set(
            TaggedItem.objects.filter(content_type__model=self.model.__name__.lower()).values_list("tag_id", flat=True)
        )
        if filters is not None:
            tags = tags.intersection(filters)
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

    def tag_cloud(self, other_model=None, queryset=None, published=True, on_site=False):
        from taggit.models import TaggedItem

        if on_site:
            queryset = queryset.on_site()
        tag_ids = self._taglist(other_model, queryset)
        kwargs = {}
        if published:
            kwargs = {
                "object_id__in": self.model.objects.published(),
                "content_type": ContentType.objects.get_for_model(self.model),
            }
        kwargs["tag_id__in"] = tag_ids
        counted_tags = dict(
            TaggedItem.objects.filter(**kwargs)
            .values("tag")
            .annotate(count=models.Count("tag"))
            .values_list("tag", "count")
        )
        tags = TaggedItem.tag_model().objects.filter(pk__in=counted_tags.keys())
        for tag in tags:
            tag.count = counted_tags[tag.pk]
        return sorted(tags, key=lambda x: -x.count)


class GenericDateQuerySet(AppHookConfigTranslatableQueryset):
    start_date_field = "date_published"
    fallback_date_field = "date_modified"
    end_date_field = "date_published_end"
    publish_field = "publish"

    def on_site(self, site=None):
        if not site:
            site = Site.objects.get_current()
        return self.filter(models.Q(sites__isnull=True) | models.Q(sites=site.pk))

    def published(self, current_site=True):
        queryset = self.published_future(current_site)
        if self.start_date_field:
            return queryset.filter(**{"%s__lte" % self.start_date_field: now()})
        else:
            return queryset

    def published_future(self, current_site=True):
        if current_site:
            queryset = self.on_site()
        else:
            queryset = self
        if self.end_date_field:
            qfilter = models.Q(**{"%s__gte" % self.end_date_field: now()}) | models.Q(
                **{"%s__isnull" % self.end_date_field: True}
            )
            queryset = queryset.filter(qfilter)
        return queryset.filter(**{self.publish_field: True})

    def archived(self, current_site=True):
        if current_site:
            queryset = self.on_site()
        else:
            queryset = self
        if self.end_date_field:
            qfilter = models.Q(**{"%s__lte" % self.end_date_field: now()})
            queryset = queryset.filter(qfilter)
        return queryset.filter(**{self.publish_field: True})

    def available(self, current_site=True):
        if current_site:
            return self.on_site().filter(**{self.publish_field: True})
        else:
            return self.filter(**{self.publish_field: True})

    def filter_by_language(self, language, current_site=True):
        if current_site:
            return self.active_translations(language_code=language).on_site()
        else:
            return self.active_translations(language_code=language)


class GenericDateTaggedManager(TaggedFilterItem, AppHookConfigTranslatableManager):
    use_for_related_fields = True

    queryset_class = GenericDateQuerySet

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)

    def published(self, current_site=True):
        return self.get_queryset().published(current_site)

    def available(self, current_site=True):
        return self.get_queryset().available(current_site)

    def archived(self, current_site=True):
        return self.get_queryset().archived(current_site)

    def published_future(self, current_site=True):
        return self.get_queryset().published_future(current_site)

    def filter_by_language(self, language, current_site=True):
        return self.get_queryset().filter_by_language(language, current_site)

    def on_site(self, site=None):
        return self.get_queryset().on_site(site)

    def get_months(self, queryset=None, current_site=True):
        """
        Get months with aggregate count (how much posts is in the month).
        Results are ordered by date.
        """
        if queryset is None:
            queryset = self.get_queryset()
        if current_site:
            queryset = queryset.on_site()
        dates_qs = queryset.values_list(queryset.start_date_field, queryset.fallback_date_field)
        dates = []
        for blog_dates in dates_qs:
            if blog_dates[0]:
                current_date = blog_dates[0]
            else:
                current_date = blog_dates[1]
            dates.append(
                (
                    current_date.year,
                    current_date.month,
                )
            )
        date_counter = Counter(dates)
        dates = set(dates)
        dates = sorted(dates, reverse=True)
        return [
            {"date": now().replace(year=year, month=month, day=1), "count": date_counter[year, month]}
            for year, month in dates
        ]
