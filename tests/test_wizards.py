# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from distutils.version import LooseVersion

import cms

from .base import BaseTest

try:
    from unittest import skipIf
except ImportError:
    from unittest2 import skipIf


class WizardTest(BaseTest):

    @skipIf(LooseVersion(cms.__version__) < LooseVersion('3.2'),
            reason='Wizards not available for django CMS < 3.2')
    def test_wizard(self):
        """
        Test that Blog wizard is present and contains all items
        """
        from cms.wizards.wizard_pool import wizard_pool
        self.get_pages()
        wizard_pool._discover()

        titles = [entry.title for entry in wizard_pool.get_entries()]
        self.assertTrue('New Blog' in titles)
        self.assertTrue('New Article' in titles)

    @skipIf(LooseVersion(cms.__version__) < LooseVersion('3.2'),
            reason='Wizards not available for django CMS < 3.2')
    def test_wizard_init(self):
        from cms.wizards.wizard_pool import wizard_pool
        from djangocms_blog.models import Post
        self.get_pages()
        wizard_pool._discover()

        wizs = [entry for entry in wizard_pool.get_entries() if entry.model == Post]
        for index, wiz in enumerate(wizs):
            app_config = self.app_config_1.pk if index == 0 else self.app_config_2.pk
            form = wiz.form(initial={'app_config': app_config})
            self.assertTrue(form.fields['app_config'].widget.attrs['disabled'])

            form = wiz.form(data={
                '1-title': 'title',
                '1-abstract': 'abstract',
                '1-categories': [self.category_1.pk],
            }, prefix=1)
            self.assertEqual(form.default_appconfig, app_config)
            self.assertTrue(form.is_valid())

    def test_wizard_import(self):
        # The following import should to fail in any django CMS version
        from djangocms_blog import cms_wizards  # NOQA
