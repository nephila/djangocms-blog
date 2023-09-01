from django.db import migrations

config_fields = [
    "url_patterns",
    "use_placeholder",
    "use_abstract",
    "use_related",
    "urlconf",
    "set_author",
    "paginate_by",
    "template_prefix",
    "menu_structure",
    "menu_empty_categories",
    "sitemap_changefreq",
    "object_type",
    "og_type",
    "og_app_id",
    "og_profile_id",
    "og_publisher",
    "og_author_url",
    "og_author",
    "twitter_type",
    "twitter_site",
    "twitter_author",
    "gplus_type",
    "gplus_author",
    "send_knock_create",
    "send_knock_update",
]


def json_to_model(apps, schema_editor):
    BlogConfig = apps.get_model("djangocms_blog", "BlogConfig")
    for config in BlogConfig.objects.all():
        if "config" in config.app_data:
            for key, value in config.app_data["config"].items():
                if key == "default_image_full":
                    config.default_image_full_id = value
                elif key == "default_image_thumbnail":
                    config.default_image_thumbnail_id = value
                elif key in config_fields:
                    setattr(config, key, value)
        # config.app_data = dict(config={})
        config.save()


def model_to_json(apps, schema_editor):
    BlogConfig = apps.get_model("djangocms_blog", "BlogConfig")
    for config in BlogConfig.objects.all():
        config.app_data = dict(
            config={
                "default_image_full": config.default_image_full_id,
                "default_image_thumbnail": config.default_image_thumbnail_id,
                "sitemap_priority": str(config.sitemap_priority),
                **{key: getattr(config, key) for key in config_fields},
            }
        )
        config.save()


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_blog", "0046_auto_20230717_2307"),
    ]

    operations = [
        migrations.RunPython(json_to_model, model_to_json, elidable=True),
        migrations.RemoveField(model_name="blogconfig", name="app_data"),
    ]
