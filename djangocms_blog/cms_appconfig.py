# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.models import AppHookConfig
from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .settings import MENU_TYPE_COMPLETE, get_setting


class BlogConfig(TranslatableModel, AppHookConfig):
    """
    Adds some translatable, per-app-instance fields.
    """
    translations = TranslatedFields(
        app_title=models.CharField(_('application title'), max_length=234),
        object_name=models.CharField(
            _('object name'), max_length=234, default=get_setting('DEFAULT_OBJECT_NAME')
        ),
    )

    class Meta:
        verbose_name = _('blog config')
        verbose_name_plural = _('blog configs')

    def get_app_title(self):
        return getattr(self, 'app_title', _('untitled'))


class BlogConfigForm(AppDataForm):
    default_published = forms.BooleanField(
        label=_('Post published by default'), required=False,
        initial=get_setting('DEFAULT_PUBLISHED')
    )
    url_patterns = forms.ChoiceField(
        label=_('Permalink structure'), required=False,
        initial=get_setting('AVAILABLE_PERMALINK_STYLES')[0][0],
        choices=get_setting('AVAILABLE_PERMALINK_STYLES')
    )
    use_placeholder = forms.BooleanField(
        label=_('Use placeholder and plugins for article body'), required=False,
        initial=get_setting('USE_PLACEHOLDER')
    )
    use_abstract = forms.BooleanField(
        label=_('Use abstract field'), required=False,
        initial=get_setting('USE_ABSTRACT')
    )
    set_author = forms.BooleanField(
        label=_('Set author'), required=False, help_text=_('Set author by default'),
        initial=get_setting('AUTHOR_DEFAULT')
    )
    paginate_by = forms.IntegerField(
        label=_('Paginate size'), required=False, initial=get_setting('PAGINATION'),
        help_text=_('When paginating list views, how many articles per page?')
    )
    template_prefix = forms.CharField(
        label=_('Template prefix'), required=False, initial='',
        help_text=_('Alternative directory to load the blog templates from')
    )
    menu_structure = forms.ChoiceField(
        label=_('Menu structure'), required=True,
        choices=get_setting('MENU_TYPES'), initial=MENU_TYPE_COMPLETE,
        help_text=_('Structure of the django CMS menu')
    )
    sitemap_changefreq = forms.ChoiceField(
        label=_('Sitemap changefreq'), required=True,
        choices=get_setting('SITEMAP_CHANGEFREQ'),
        initial=get_setting('SITEMAP_CHANGEFREQ_DEFAULT'),
        help_text=_('Changefreq attribute for sitemap items')
    )
    sitemap_priority = forms.CharField(
        label=_('Sitemap priority'), required=True,
        initial=get_setting('SITEMAP_PRIORITY_DEFAULT'),
        help_text=_('Priority attribute for sitemap items')
    )
    object_type = forms.ChoiceField(
        label=_('Object type'), required=False,
        choices=get_setting('TYPES'), initial=get_setting('TYPE')
    )
    og_type = forms.ChoiceField(
        label=_('Facebook type'), required=False,
        choices=get_setting('FB_TYPES'), initial=get_setting('FB_TYPE')
    )
    og_app_id = forms.CharField(
        max_length=200, label=_('Facebook application ID'), required=False,
        initial=get_setting('FB_PROFILE_ID')
    )
    og_profile_id = forms.CharField(
        max_length=200, label=_('Facebook profile ID'), required=False,
        initial=get_setting('FB_PROFILE_ID')
    )
    og_publisher = forms.CharField(
        max_length=200, label=_('Facebook page URL'), required=False,
        initial=get_setting('FB_PUBLISHER')
    )
    og_author_url = forms.CharField(
        max_length=200, label=_('Facebook author URL'), required=False,
        initial=get_setting('FB_AUTHOR_URL')
    )
    og_author = forms.CharField(
        max_length=200, label=_('Facebook author'), required=False,
        initial=get_setting('FB_AUTHOR')
    )
    twitter_type = forms.ChoiceField(
        label=_('Twitter type'), required=False,
        choices=get_setting('TWITTER_TYPES'), initial=get_setting('TWITTER_TYPE')
    )
    twitter_site = forms.CharField(
        max_length=200, label=_('Twitter site handle'), required=False,
        initial=get_setting('TWITTER_SITE')
    )
    twitter_author = forms.CharField(
        max_length=200, label=_('Twitter author handle'), required=False,
        initial=get_setting('TWITTER_AUTHOR')
    )
    gplus_type = forms.ChoiceField(
        label=_('Google+ type'), required=False,
        choices=get_setting('GPLUS_TYPES'), initial=get_setting('GPLUS_TYPE')
    )
    gplus_author = forms.CharField(
        max_length=200, label=_('Google+ author name'), required=False,
        initial=get_setting('GPLUS_AUTHOR')
    )

    send_knock_create = forms.BooleanField(
        label=_('Send notifications on post publish'), required=False, initial=False,
        help_text=_('Emits a desktop notification -if enabled- when publishing a new post')
    )
    send_knock_update = forms.BooleanField(
        label=_('Send notifications on post update'), required=False, initial=False,
        help_text=_('Emits a desktop notification -if enabled- when editing a published post')
    )
setup_config(BlogConfigForm, BlogConfig)
