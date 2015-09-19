# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BlogConfigTranslation'
        db.create_table('djangocms_blog_blogconfig_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=15)),
            ('app_title', self.gf('django.db.models.fields.CharField')(max_length=234)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangocms_blog.BlogConfig'], related_name='translations', null=True)),
        ))
        db.send_create_signal('djangocms_blog', ['BlogConfigTranslation'])

        # Adding unique constraint on 'BlogConfigTranslation', fields ['language_code', 'master']
        db.create_unique('djangocms_blog_blogconfig_translation', ['language_code', 'master_id'])

        # Adding model 'BlogConfig'
        db.create_table('djangocms_blog_blogconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('namespace', self.gf('django.db.models.fields.CharField')(default=None, max_length=100, unique=True)),
            ('app_data', self.gf('app_data.fields.AppDataField')(default='{}')),
        ))
        db.send_create_signal('djangocms_blog', ['BlogConfig'])

        # Adding model 'GenericBlogPlugin'
        db.create_table('djangocms_blog_genericblogplugin', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(primary_key=True, to=orm['cms.CMSPlugin'], unique=True)),
            ('app_config', self.gf('aldryn_apphooks_config.fields.AppHookConfigField')(blank=True, null=True, to=orm['djangocms_blog.BlogConfig'])),
        ))
        db.send_create_signal('djangocms_blog', ['GenericBlogPlugin'])

        # Adding field 'AuthorEntriesPlugin.app_config'
        db.add_column('djangocms_blog_authorentriesplugin', 'app_config',
                      self.gf('aldryn_apphooks_config.fields.AppHookConfigField')(default=None, blank=True, null=True, to=orm['djangocms_blog.BlogConfig']),
                      keep_default=False)

        # Adding field 'Post.app_config'
        db.add_column('djangocms_blog_post', 'app_config',
                      self.gf('aldryn_apphooks_config.fields.AppHookConfigField')(to=orm['djangocms_blog.BlogConfig'], null=True, default=None),
                      keep_default=False)

        # Adding field 'BlogCategory.app_config'
        db.add_column('djangocms_blog_blogcategory', 'app_config',
                      self.gf('aldryn_apphooks_config.fields.AppHookConfigField')(to=orm['djangocms_blog.BlogConfig'], null=True, default=None),
                      keep_default=False)

        # Adding field 'LatestPostsPlugin.app_config'
        db.add_column('djangocms_blog_latestpostsplugin', 'app_config',
                      self.gf('aldryn_apphooks_config.fields.AppHookConfigField')(default=None, null=True, blank=True, to=orm['djangocms_blog.BlogConfig']),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'BlogConfigTranslation', fields ['language_code', 'master']
        db.delete_unique('djangocms_blog_blogconfig_translation', ['language_code', 'master_id'])

        # Deleting model 'BlogConfigTranslation'
        db.delete_table('djangocms_blog_blogconfig_translation')

        # Deleting model 'BlogConfig'
        db.delete_table('djangocms_blog_blogconfig')

        # Deleting model 'GenericBlogPlugin'
        db.delete_table('djangocms_blog_genericblogplugin')

        # Deleting field 'AuthorEntriesPlugin.app_config'
        db.delete_column('djangocms_blog_authorentriesplugin', 'app_config_id')

        # Deleting field 'Post.app_config'
        db.delete_column('djangocms_blog_post', 'app_config_id')

        # Deleting field 'BlogCategory.app_config'
        db.delete_column('djangocms_blog_blogcategory', 'app_config_id')

        # Deleting field 'LatestPostsPlugin.app_config'
        db.delete_column('djangocms_blog_latestpostsplugin', 'app_config_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'related_name': "'user_set'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'related_name': "'user_set'", 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
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
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
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
        'cmsplugin_filer_image.thumbnailoption': {
            'Meta': {'object_name': 'ThumbnailOption', 'ordering': "('width', 'height')"},
            'crop': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upscale': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)", 'db_table': "'django_content_type'", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangocms_blog.authorentriesplugin': {
            'Meta': {'object_name': 'AuthorEntriesPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogConfig']"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['cms.CMSPlugin']", 'unique': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'djangocms_blog.blogcategory': {
            'Meta': {'object_name': 'BlogCategory'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'to': "orm['djangocms_blog.BlogConfig']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogCategory']", 'null': 'True'})
        },
        'djangocms_blog.blogcategorytranslation': {
            'Meta': {'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]", 'object_name': 'BlogCategoryTranslation', 'db_table': "'djangocms_blog_blogcategory_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangocms_blog.BlogCategory']", 'related_name': "'translations'", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'blank': 'True', 'max_length': '50'})
        },
        'djangocms_blog.blogconfig': {
            'Meta': {'object_name': 'BlogConfig'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'unique': 'True'}),
            'paginate_by': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'set_author': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangocms_blog.blogconfigtranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'BlogConfigTranslation', 'db_table': "'djangocms_blog_blogconfig_translation'"},
            'app_title': ('django.db.models.fields.CharField', [], {'max_length': '234'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangocms_blog.BlogConfig']", 'related_name': "'translations'", 'null': 'True'})
        },
        'djangocms_blog.genericblogplugin': {
            'Meta': {'object_name': 'GenericBlogPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogConfig']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['cms.CMSPlugin']", 'unique': 'True'})
        },
        'djangocms_blog.latestpostsplugin': {
            'Meta': {'object_name': 'LatestPostsPlugin'},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'blank': 'True', 'to': "orm['djangocms_blog.BlogConfig']"}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['djangocms_blog.BlogCategory']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['cms.CMSPlugin']", 'unique': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'djangocms_blog.post': {
            'Meta': {'object_name': 'Post', 'ordering': "('-date_published', '-date_created')"},
            'app_config': ('aldryn_apphooks_config.fields.AppHookConfigField', [], {'to': "orm['djangocms_blog.BlogConfig']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'djangocms_blog_post_author'", 'to': "orm['auth.User']", 'null': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['djangocms_blog.BlogCategory']", 'related_name': "'blog_posts'"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'related_name': "'post_content'", 'null': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_published_end': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'djangocms_blog_post_image'", 'to': "orm['filer.Image']", 'null': 'True'}),
            'main_image_full': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'djangocms_blog_post_full'", 'to': "orm['cmsplugin_filer_image.ThumbnailOption']", 'null': 'True'}),
            'main_image_thumbnail': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'blank': 'True', 'related_name': "'djangocms_blog_post_thumbnail'", 'to': "orm['cmsplugin_filer_image.ThumbnailOption']", 'null': 'True'}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['sites.Site']", 'null': 'True'})
        },
        'djangocms_blog.posttranslation': {
            'Meta': {'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]", 'object_name': 'PostTranslation', 'db_table': "'djangocms_blog_post_translation'"},
            'abstract': ('djangocms_text_ckeditor.fields.HTMLField', [], {'blank': 'True', 'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangocms_blog.Post']", 'related_name': "'translations'", 'null': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'meta_title': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '255', 'default': "''"}),
            'post_text': ('djangocms_text_ckeditor.fields.HTMLField', [], {'blank': 'True', 'default': "''"}),
            'slug': ('django.db.models.fields.SlugField', [], {'blank': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_files'", 'to': "orm['filer.Folder']", 'null': 'True'}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '255', 'default': "''"}),
            'original_filename': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '255', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_files'", 'to': "orm['auth.User']", 'null': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'related_name': "'polymorphic_filer.file_set+'", 'null': 'True'}),
            'sha1': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '40', 'default': "''"}),
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
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filer_owned_folders'", 'to': "orm['auth.User']", 'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'to': "orm['filer.Folder']", 'null': 'True'}),
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
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'to': "orm['filer.File']", 'unique': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '64', 'default': 'None', 'null': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'", 'object_name': 'Site'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['djangocms_blog']
