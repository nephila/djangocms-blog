from django.db import migrations, models

from djangocms_blog.settings import get_setting

BLOG_PLUGIN_TEMPLATE_FOLDERS = get_setting("PLUGIN_TEMPLATE_FOLDERS")


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_blog", "0023_auto_20160626_1539"),
    ]

    operations = [
        migrations.AddField(
            model_name="authorentriesplugin",
            name="template_folder",
            field=models.CharField(
                default=BLOG_PLUGIN_TEMPLATE_FOLDERS[0][0],
                verbose_name="Plugin template",
                max_length=200,
                help_text="Select plugin template to load for this instance",
                choices=BLOG_PLUGIN_TEMPLATE_FOLDERS,
            ),
        ),
        migrations.AddField(
            model_name="genericblogplugin",
            name="template_folder",
            field=models.CharField(
                default=BLOG_PLUGIN_TEMPLATE_FOLDERS[0][0],
                verbose_name="Plugin template",
                max_length=200,
                help_text="Select plugin template to load for this instance",
                choices=BLOG_PLUGIN_TEMPLATE_FOLDERS,
            ),
        ),
        migrations.AddField(
            model_name="latestpostsplugin",
            name="template_folder",
            field=models.CharField(
                default=BLOG_PLUGIN_TEMPLATE_FOLDERS[0][0],
                verbose_name="Plugin template",
                max_length=200,
                help_text="Select plugin template to load for this instance",
                choices=BLOG_PLUGIN_TEMPLATE_FOLDERS,
            ),
        ),
    ]
