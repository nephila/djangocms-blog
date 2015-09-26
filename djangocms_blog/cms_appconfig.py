# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.models import AppHookConfig
from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .settings import get_setting


class BlogConfig(TranslatableModel, AppHookConfig):
    """
    Adds some translatable, per-app-instance fields.
    """
    translations = TranslatedFields(
        app_title=models.CharField(_('application title'), max_length=234),
    )

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
    object_type = forms.ChoiceField(
        label=_('Object type'), required=False,
        choices=get_setting('TYPES'), initial=get_setting('TYPE')
    )
    og_type = forms.ChoiceField(
        label=_('Facebook type'), required=False,
        choices=get_setting('FB_TYPES'), initial=get_setting('FB_TYPES')[0][0]
    )
    og_app_id = forms.CharField(
        max_length=200, label=_('Facebook application ID'), required=False,
    )
    og_profile_id = forms.CharField(
        max_length=200, label=_('Facebook profile ID'), required=False,
    )
    og_publisher = forms.CharField(
        max_length=200, label=_('Facebook page URL'), required=False
    )
    og_author_url = forms.CharField(
        max_length=200, label=_('Facebook author URL'), required=False
    )
    twitter_type = forms.ChoiceField(
        label=_('Twitter type'), required=False,
        choices=get_setting('TWITTER_TYPES'), initial=get_setting('TWITTER_TYPES')[0][0]
    )
    twitter_site = forms.CharField(
        max_length=200, label=_('Twitter site handle'), required=False
    )
    twitter_author = forms.CharField(
        max_length=200, label=_('Twitter author handle'), required=False
    )
    gplus_type = forms.ChoiceField(
        label=_('Google+ type'), required=False,
        choices=get_setting('GPLUS_TYPES'), initial=get_setting('GPLUS_TYPES')[0][0]
    )
    gplus_author = forms.CharField(
        max_length=200, label=_('Google+ author name'), required=False
    )
setup_config(BlogConfigForm, BlogConfig)
