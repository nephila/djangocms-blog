import aldryn_apphooks_config.fields
import django.utils.timezone
from django.db import migrations, models

from djangocms_blog.settings import get_setting


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_blog", "0010_auto_20150923_1151"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogconfigtranslation",
            name="object_name",
            field=models.CharField(
                verbose_name="object name", default=get_setting("DEFAULT_OBJECT_NAME"), max_length=234
            ),
        ),
        migrations.AlterField(
            model_name="authorentriesplugin",
            name="app_config",
            field=aldryn_apphooks_config.fields.AppHookConfigField(
                blank=True,
                help_text="When selecting a value, the form is reloaded to get the updated default",
                to="djangocms_blog.BlogConfig",
                verbose_name="app. config",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="blogcategory",
            name="app_config",
            field=aldryn_apphooks_config.fields.AppHookConfigField(
                help_text="When selecting a value, the form is reloaded to get the updated default",
                to="djangocms_blog.BlogConfig",
                verbose_name="app. config",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="genericblogplugin",
            name="app_config",
            field=aldryn_apphooks_config.fields.AppHookConfigField(
                blank=True,
                help_text="When selecting a value, the form is reloaded to get the updated default",
                to="djangocms_blog.BlogConfig",
                verbose_name="app. config",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="latestpostsplugin",
            name="app_config",
            field=aldryn_apphooks_config.fields.AppHookConfigField(
                blank=True,
                help_text="When selecting a value, the form is reloaded to get the updated default",
                to="djangocms_blog.BlogConfig",
                verbose_name="app. config",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="app_config",
            field=aldryn_apphooks_config.fields.AppHookConfigField(
                help_text="When selecting a value, the form is reloaded to get the updated default",
                to="djangocms_blog.BlogConfig",
                verbose_name="app. config",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="date_published",
            field=models.DateTimeField(verbose_name="published since", default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="post",
            name="date_published_end",
            field=models.DateTimeField(blank=True, verbose_name="published until", null=True),
        ),
    ]
