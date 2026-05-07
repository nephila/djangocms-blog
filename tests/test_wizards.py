import sys

from django.http import QueryDict
from djangocms_text_ckeditor.models import Text

from djangocms_blog.compat import CMS_4_PLUS
from djangocms_blog.models import BlogCategory

from .base import BaseTest


def _get_wizard_entries():
    if CMS_4_PLUS:
        from cms.wizards.helpers import get_entries

        return get_entries()
    from cms.wizards.wizard_pool import wizard_pool

    return wizard_pool.get_entries()


def _reset_wizard_pool():
    if CMS_4_PLUS:
        from django.apps import apps

        apps.get_app_config("cms").cms_extension.wizards.clear()
    else:
        from cms.wizards.wizard_pool import wizard_pool

        wizard_pool._reset()


class WizardTest(BaseTest):
    def setUp(self):
        delete = [
            "djangocms_blog",
            "djangocms_blog.cms_wizards",
        ]
        for module in delete:
            if module in sys.modules:
                del sys.modules[module]
        _reset_wizard_pool()
        super().setUp()
        # django CMS 3.x compatibility: in CMS 3.x wizard_pool had lazy re-discovery
        # so deleting the module from sys.modules was enough to force re-registration on
        # the next get_entries() call.  In CMS 4.x the pool is a plain dict with no
        # auto-rediscovery; we must explicitly reimport after clearing it.
        # When CMS 3.x support is dropped, move the import_module call outside the
        # `if CMS_4_PLUS:` guard (it's a no-op on a fresh import in any version).
        if CMS_4_PLUS:
            import importlib

            importlib.import_module("djangocms_blog.cms_wizards")

    def get_querydict(self, source):
        tmp = QueryDict(mutable=True)
        tmp.update(source)
        tmp._mutable = False
        return tmp

    def test_wizard(self):
        """
        Test that Blog wizard is present and contains all items
        """

        self.get_pages()

        titles = [entry.title for entry in _get_wizard_entries()]
        self.assertTrue("New Blog" in titles)
        self.assertTrue("New Article" in titles)

    def test_wizard_init(self):
        from cms.utils.permissions import current_user

        from djangocms_blog.models import Post

        self.get_pages()

        cat_1 = BlogCategory.objects.create(name="category 1 - blog 1", app_config=self.app_config_1)
        cat_2 = BlogCategory.objects.create(name="category 1 - blog 2", app_config=self.app_config_2)
        self.app_config_2.app_data.config.use_placeholder = False
        self.app_config_2.save()
        cats = {
            self.app_config_1.pk: cat_1,
            self.app_config_2.pk: cat_2,
        }
        with current_user(self.user_staff):
            wizs = [entry for entry in _get_wizard_entries() if entry.model == Post]
            for index, wiz in enumerate(wizs):
                app_config = self.app_config_1.pk if wiz.title == "New Blog" else self.app_config_2.pk
                form = wiz.form()
                self.assertTrue(form.initial.get("app_config", False), app_config)
                self.assertTrue(form.fields["app_config"].widget.attrs["disabled"])

                form = wiz.form(
                    data=self.get_querydict(
                        {
                            "1-title": "title{}".format(index),
                            "1-abstract": "abstract{}".format(index),
                            "1-categories": cats[app_config].pk,
                            "1-post_text": "Random text",
                        }
                    ),
                    prefix=1,
                )
                self.assertEqual(form.default_appconfig, app_config)
                self.assertTrue(form.is_valid())
                self.assertEqual(form.cleaned_data["app_config"].pk, app_config)
                instance = form.save()
                self.assertEqual(instance.author, self.user_staff)
                self.assertEqual(instance.post_text, "Random text")
                if form.cleaned_data["app_config"].use_placeholder:
                    self.assertEqual(instance.content.get_plugins().filter(plugin_type="TextPlugin").count(), 1)
                    plugin = Text.objects.get(pk=instance.content.get_plugins().get(plugin_type="TextPlugin").pk)
                    self.assertEqual(plugin.body, "Random text")
                else:
                    self.assertEqual(instance.content.get_plugins().filter(plugin_type="TextPlugin").count(), 0)

            with self.settings(BLOG_AUTHOR_DEFAULT="normal"):
                for index, wiz in enumerate(wizs):
                    app_config = self.app_config_1.pk if wiz.title == "New Blog" else self.app_config_2.pk
                    form = wiz.form(
                        data=self.get_querydict(
                            {
                                "1-title": "title-2{}".format(index),
                                "1-abstract": "abstract-2{}".format(index),
                                "1-categories": cats[app_config].pk,
                            }
                        ),
                        prefix=1,
                    )
                    self.assertEqual(form.default_appconfig, app_config)
                    self.assertTrue(form.is_valid())
                    self.assertEqual(form.cleaned_data["app_config"].pk, app_config)
                    instance = form.save()
                    self.assertEqual(instance.author, self.user_normal)
        self.app_config_2.app_data.config.use_placeholder = True
        self.app_config_2.save()

    def test_wizard_duplicate_slug(self):
        from cms.utils.permissions import current_user

        from djangocms_blog.models import Post

        self.get_pages()
        cat_2 = BlogCategory.objects.create(name="category 1 - blog 2", app_config=self.app_config_2)

        with current_user(self.user_staff):
            wiz = None
            for wiz in _get_wizard_entries():
                if wiz.model == Post and wiz.title == "New Blog":
                    break
            form = wiz.form(
                data=self.get_querydict(
                    {"1-title": "title article", "1-abstract": "abstract article", "1-categories": self.category_1.pk}
                ),
                prefix=1,
            )
            self.assertEqual(form.default_appconfig, self.app_config_1.pk)
            self.assertTrue(form.is_valid())
            instance1 = form.save()
            self.assertEqual(instance1.slug, "title-article")

            form = wiz.form(
                data=self.get_querydict(
                    {"1-title": "title article", "1-abstract": "abstract article", "1-categories": self.category_1.pk}
                ),
                prefix=1,
            )
            self.assertEqual(form.default_appconfig, self.app_config_1.pk)
            self.assertTrue(form.is_valid())
            instance2 = form.save()
            self.assertEqual(instance2.slug, "title-article-1")

            for wiz in _get_wizard_entries():
                if wiz.model == Post and wiz.title == "New Article":
                    break
            form = wiz.form(
                data=self.get_querydict(
                    {"1-title": "title article", "1-abstract": "abstract article", "1-categories": cat_2.pk}
                ),
                prefix=1,
            )
            self.assertEqual(form.default_appconfig, self.app_config_2.pk)
            self.assertTrue(form.is_valid())
            instance3 = form.save()
            self.assertEqual(instance3.slug, "title-article-2")

    def test_wizard_init_categories_check(self):
        from cms.utils.permissions import current_user

        from djangocms_blog.models import Post

        self.get_pages()

        with current_user(self.user_staff):
            wiz = None
            for wiz in _get_wizard_entries():
                if wiz.model == Post and wiz.title == "New Article":
                    break
            form = wiz.form(
                data=self.get_querydict(
                    {"1-title": "title article", "1-abstract": "abstract article", "1-categories": self.category_1.pk}
                ),
                prefix=1,
            )
            self.assertEqual(form.default_appconfig, self.app_config_2.pk)
            self.assertFalse(form.is_valid())
            self.assertTrue("categories" in form.errors.keys())

    def test_wizard_import(self):
        # The following import should not fail in any django CMS version
        pass
