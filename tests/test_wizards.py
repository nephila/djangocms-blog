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
