"""django CMS 4.x compatibility migration.

In CMS 3.x, ``Post`` carries three ``PlaceholderField`` columns
(``media``, ``content``, ``liveblog``) — each is a real ``ForeignKey`` to
``cms.Placeholder``.  In CMS 4.x, ``Post`` instead carries a single
``PlaceholderRelationField`` (a generic relation, no DB column) and the three
attributes are exposed as ``@cached_property`` resolvers — see
``djangocms_blog/models.py``.

Without this migration ``manage.py makemigrations`` would generate a destructive
diff on every CMS 4.x install (because the model says the FKs don't exist while
migration state still has them).  This migration aligns migration state with the
runtime model on CMS 4.x and is a no-op on CMS 3.x.

Note: this is a *schema* migration only.  If you are upgrading an existing
CMS 3.x database to CMS 4.x, write a separate data migration to copy the
existing ``media_id`` / ``content_id`` / ``liveblog_id`` references into the
new generic placeholders relation *before* applying this one.  Fresh CMS 4.x
installs do not need that step.
"""

from django.db import migrations

from djangocms_blog.compat import CMS_4_PLUS


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_blog", "0042_alter_authorentriesplugin_cmsplugin_ptr_and_more"),
    ]

    if CMS_4_PLUS:
        operations = [
            migrations.RemoveField(model_name="post", name="media"),
            migrations.RemoveField(model_name="post", name="content"),
            migrations.RemoveField(model_name="post", name="liveblog"),
        ]
    else:
        operations = []
