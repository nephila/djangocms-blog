# -*- coding: utf-8 -*-
from djangocms_blog.models import thumbnail_model
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from djangocms_blog.settings import get_setting


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BlogConfigTranslation.object_name'
        db.add_column('djangocms_blog_blogconfig_translation', 'object_name',
                      self.gf('django.db.models.fields.CharField')(default=get_setting('DEFAULT_OBJECT_NAME'), max_length=234),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BlogConfigTranslation.object_name'
        db.delete_column('djangocms_blog_blogconfig_translation', 'object_name')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'related_name': "'user_set'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Permission']", 'related_name': "'user_set'", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['cms.CMSPlugin']", 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        thumbnail_model: {
            'Meta': {'object_name': 'ThumbnailOption', 'ordering': "('width', 'height')"},
            'crop': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upscale': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'object_name': 'ContentType', 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangocms_blog.authorentriesplugin': {
            'Meta': {'object_name': 'AuthorEntriesPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'blank': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['cms.CMSPlugin']", 'unique': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'djangocms_blog.blogcategory': {
            'Meta': {'object_name': 'BlogCategory'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogConfig']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogCategory']", 'blank': 'True'})
        },
        'djangocms_blog.blogcategorytranslation': {
            'Meta': {'db_table': "'djangocms_blog_blogcategory_translation'", 'object_name': 'BlogCategoryTranslation', 'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogCategory']", 'related_name': "'translations'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'blank': 'True', 'max_length': '50'})
        },
        'djangocms_blog.blogconfig': {
            'Meta': {'object_name': 'BlogConfig'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'default': 'None', 'unique': 'True', 'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangocms_blog.blogconfigtranslation': {
            'Meta': {'db_table': "'djangocms_blog_blogconfig_translation'", 'object_name': 'BlogConfigTranslation', 'unique_together': "[('language_code', 'master')]"},
            'app_title': ('django.db.models.fields.CharField', [], {'max_length': '234'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'related_name': "'translations'"}),
            'object_name': ('django.db.models.fields.CharField', [], {'default': "'Post'", 'max_length': '234'})
        },
        'djangocms_blog.genericblogplugin': {
            'Meta': {'object_name': 'GenericBlogPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['cms.CMSPlugin']", 'unique': 'True'})
        },
        'djangocms_blog.latestpostsplugin': {
            'Meta': {'object_name': 'LatestPostsPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogConfig']", 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['djangocms_blog.BlogCategory']", 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['cms.CMSPlugin']", 'unique': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'djangocms_blog.post': {
            'Meta': {'object_name': 'Post', 'ordering': "('-date_published', '-date_created')"},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'null': 'True', 'to': "orm['djangocms_blog.BlogConfig']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['auth.User']", 'related_name': "'djangocms_blog_post_author'", 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['djangocms_blog.BlogCategory']", 'related_name': "'blog_posts'"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['cms.Placeholder']", 'related_name': "'post_content'"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_published_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['filer.Image']", 'related_name': "'djangocms_blog_post_image'", 'blank': 'True'}),
            'main_image_full': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm[thumbnail_model]", 'related_name': "'djangocms_blog_post_full'", 'blank': 'True'}),
            'main_image_thumbnail': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm[thumbnail_model]", 'related_name': "'djangocms_blog_post_thumbnail'", 'blank': 'True'}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sites.Site']", 'blank': 'True'})
        },
        'djangocms_blog.posttranslation': {
            'Meta': {'db_table': "'djangocms_blog_post_translation'", 'object_name': 'PostTranslation', 'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]"},
            'abstract': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['djangocms_blog.Post']", 'related_name': "'translations'"}),
            'meta_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '255'}),
            'post_text': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'blank': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'null': 'True', 'blank': 'True', 'max_length': '255'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['filer.Folder']", 'related_name': "'all_files'", 'blank': 'True'}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '255'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['auth.User']", 'related_name': "'owned_files'", 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['contenttypes.ContentType']", 'related_name': "'polymorphic_filer.file_set+'"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '40'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.folder': {
            'Meta': {'object_name': 'Folder', 'ordering': "('name',)", 'unique_together': "(('parent', 'name'),)"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['auth.User']", 'related_name': "'filer_owned_folders'", 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['filer.Folder']", 'related_name': "'children'", 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.image': {
            'Meta': {'object_name': 'Image'},
            '_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '255'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '255'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '255'}),
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['filer.File']", 'unique': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'null': 'True', 'blank': 'True', 'max_length': '64'})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'", 'object_name': 'Site', 'ordering': "('domain',)"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['djangocms_blog']
