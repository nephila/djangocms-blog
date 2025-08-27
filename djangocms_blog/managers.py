from collections import Counter

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
        return self.get_queryset().filter(post__tags__in=tags).distinct()

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


class SiteQuerySet(models.QuerySet):

    def on_site(self, site=None):
        if not site:
            site = Site.objects.get_current()
        return self.filter(models.Q(post__sites__isnull=True) | models.Q(post__sites=site.pk))

    def filter_by_language(self, language, current_site=True):
        if current_site:
            return self.filter(language=language).on_site()
        else:
            return self.filter(language=language)


class AdminSiteQuerySet(SiteQuerySet):
    def current_content(self, **kwargs):
        """If a versioning package is installed, this returns the currently valid content
        that matches the filter given in kwargs. Used to find content to be copied, e.g..
        Without versioning every page is current."""
        return self.filter(**kwargs)

    def latest_content(self, **kwargs):
        """If a versioning package is installed, returns the latest version that matches the
        filter given in kwargs including discared or unpublished page content. Without versioning
        every page content is the latest."""
        return self.filter(**kwargs)


class GenericDateTaggedManager(TaggedFilterItem, models.Manager):
    use_for_related_fields = True

    queryset_class = SiteQuerySet

    def get_queryset(self, *args, **kwargs):
        return self.queryset_class(model=self.model, using=self._db, hints=self._hints)

    def published(self, current_site=True):
        return self.get_queryset().published(current_site)

    def published_on_rss(self, current_site=True):
        return self.get_queryset().published_on_rss(current_site)

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
        Get months with aggregate count (how many posts is in the month).
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


class AdminDateTaggedManager(GenericDateTaggedManager):
    queryset_class = AdminSiteQuerySet

    def current_content(self, **kwargs):
        """Syntactic sugar: admin_manager.current_content()"""
        return self.get_queryset().current_content(**kwargs)

    def latest_content(self, **kwargs):
        """Syntactic sugar: admin_manager.latest_content()"""
        return self.get_queryset().latest_content(**kwargs)
