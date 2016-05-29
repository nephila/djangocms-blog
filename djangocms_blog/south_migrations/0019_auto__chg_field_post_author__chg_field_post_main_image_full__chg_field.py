# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from djangocms_blog.models import thumbnail_model
from django.contrib.auth import get_user_model

User = get_user_model()
user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)


class Migration(SchemaMigration):

    if 'cmsplugin_filer' not in thumbnail_model:
        depends_on = [
            ('djangocms_blog', '0018_auto__chg_field_post_main_image_full__chg_field_post_main_image_thumbn'),
            ('cmsplugin_filer_image', '0013_mv_thumbnailoption_to_filer'),
            ('filer', '0015_auto__add_thumbnailoption'),
        ]
        needed_by = [
            ('cmsplugin_filer_image', '0014_auto__del_thumbnailoption__chg_field_filerimage_thumbnail_option'),
        ]
    else:
        depends_on = [
            ('djangocms_blog', '0018_auto__chg_field_post_main_image_full__chg_field_post_main_image_thumbn'),
        ]


    def forwards(self, orm):

        # Changing field 'Post.author'
        db.alter_column('djangocms_blog_post', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['test_utils.CustomUser']))

        # Changing field 'Post.main_image_full'
        db.alter_column('djangocms_blog_post', 'main_image_full_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, null=True, to=orm[thumbnail_model]))

        # Changing field 'Post.main_image_thumbnail'
        db.alter_column('djangocms_blog_post', 'main_image_thumbnail_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, null=True, to=orm[thumbnail_model]))

    def backwards(self, orm):

        # Changing field 'Post.author'
        db.alter_column('djangocms_blog_post', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm[user_orm_label]))

        # Changing field 'Post.main_image_full'
        db.alter_column('djangocms_blog_post', 'main_image_full_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, null=True, to=orm[thumbnail_model]))

        # Changing field 'Post.main_image_thumbnail'
        db.alter_column('djangocms_blog_post', 'main_image_thumbnail_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, null=True, to=orm[thumbnail_model]))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        user_model_label: {
            'Meta': {'object_name': User.__name__, 'db_table': "'%s'" % User._meta.db_table},
            'date_joined': (
            'django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': (
            'django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': (
            'django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True',
                        'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': (
            'django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': (
            'django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                 {'symmetrical': 'False', 'related_name': "u'user_set'",
                                  'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': (
            'django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['cms.CMSPlugin']", 'null': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'blank': 'True', 'null': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'", 'ordering': "('name',)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        thumbnail_model: {
            'Meta': {'ordering': "('width', 'height')", 'object_name': 'ThumbnailOption'},
            'crop': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upscale': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'djangocms_blog.authorentriesplugin': {
            'Meta': {'object_name': 'AuthorEntriesPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'null': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['test_utils.CustomUser']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'djangocms_blog.blogcategory': {
            'Meta': {'object_name': 'BlogCategory'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'to': "orm['djangocms_blog.BlogConfig']", 'null': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogCategory']", 'null': 'True'})
        },
        'djangocms_blog.blogcategorytranslation': {
            'Meta': {'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]", 'object_name': 'BlogCategoryTranslation', 'db_table': "'djangocms_blog_blogcategory_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogCategory']", 'related_name': "'translations'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'blank': 'True', 'max_length': '255'})
        },
        'djangocms_blog.blogconfig': {
            'Meta': {'object_name': 'BlogConfig'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'default': 'None', 'unique': 'True', 'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangocms_blog.blogconfigtranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'BlogConfigTranslation', 'db_table': "'djangocms_blog_blogconfig_translation'"},
            'app_title': ('django.db.models.fields.CharField', [], {'max_length': '234'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'related_name': "'translations'"}),
            'object_name': ('django.db.models.fields.CharField', [], {'default': "'Article'", 'max_length': '234'})
        },
        'djangocms_blog.genericblogplugin': {
            'Meta': {'object_name': 'GenericBlogPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'null': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'})
        },
        'djangocms_blog.latestpostsplugin': {
            'Meta': {'object_name': 'LatestPostsPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'null': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['djangocms_blog.BlogCategory']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'djangocms_blog.post': {
            'Meta': {'object_name': 'Post', 'ordering': "('-date_published', '-date_created')"},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'to': "orm['djangocms_blog.BlogConfig']", 'null': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['test_utils.CustomUser']", 'related_name': "'djangocms_blog_post_author'"}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['djangocms_blog.BlogCategory']", 'related_name': "'blog_posts'"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['cms.Placeholder']", 'related_name': "'post_content'"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'date_published_end': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True', 'to': "orm['filer.Image']", 'related_name': "'djangocms_blog_post_image'"}),
            'main_image_full': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True', 'to': u"orm['%s']" % thumbnail_model, 'related_name': "'djangocms_blog_post_full'"}),
            'main_image_thumbnail': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'null': 'True', 'to': u"orm['%s']" % thumbnail_model, 'related_name': "'djangocms_blog_post_thumbnail'"}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['sites.Site']"})
        },
        'djangocms_blog.posttranslation': {
            'Meta': {'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]", 'object_name': 'PostTranslation', 'db_table': "'djangocms_blog_post_translation'"},
            'abstract': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['djangocms_blog.Post']", 'related_name': "'translations'"}),
            'meta_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '255'}),
            'post_text': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'blank': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['filer.Folder']", 'related_name': "'all_files'"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '255'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['test_utils.CustomUser']", 'related_name': "'owned_files'"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['contenttypes.ContentType']", 'related_name': "'polymorphic_filer.file_set+'"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '40'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'})
        },
        'filer.folder': {
            'Meta': {'unique_together': "(('parent', 'name'),)", 'object_name': 'Folder', 'ordering': "('name',)"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['test_utils.CustomUser']", 'related_name': "'filer_owned_folders'"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['filer.Folder']", 'related_name': "'children'"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'})
        },
        'filer.image': {
            'Meta': {'object_name': 'Image'},
            '_height': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['filer.File']", 'unique': 'True', 'primary_key': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '64'})
        },
        'sites.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'django_site'", 'ordering': "('domain',)"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'test_utils.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Group']", 'related_name': "'user_set'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']", 'related_name': "'user_set'"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['djangocms_blog']
