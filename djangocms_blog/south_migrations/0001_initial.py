# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.utils import timezone
from djangocms_blog.models import thumbnail_model
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


User = get_user_model()
user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BlogCategoryTranslation'
        db.create_table(u'djangocms_blog_blogcategory_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['djangocms_blog.BlogCategory'])),
        ))
        db.send_create_signal(u'djangocms_blog', ['BlogCategoryTranslation'])

        # Adding unique constraint on 'BlogCategoryTranslation', fields ['language_code', 'slug']
        db.create_unique(u'djangocms_blog_blogcategory_translation', ['language_code', 'slug'])

        # Adding unique constraint on 'BlogCategoryTranslation', fields ['language_code', 'master']
        db.create_unique(u'djangocms_blog_blogcategory_translation', ['language_code', 'master_id'])

        # Adding model 'BlogCategory'
        db.create_table(u'djangocms_blog_blogcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangocms_blog.BlogCategory'], null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'djangocms_blog', ['BlogCategory'])

        # Adding model 'PostTranslation'
        db.create_table(u'djangocms_blog_post_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('abstract', self.gf('djangocms_text_ckeditor.fields.HTMLField')()),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['djangocms_blog.Post'])),
        ))
        db.send_create_signal(u'djangocms_blog', ['PostTranslation'])

        # Adding unique constraint on 'PostTranslation', fields ['language_code', 'slug']
        db.create_unique(u'djangocms_blog_post_translation', ['language_code', 'slug'])

        # Adding unique constraint on 'PostTranslation', fields ['language_code', 'master']
        db.create_unique(u'djangocms_blog_post_translation', ['language_code', 'master_id'])

        # Adding model 'Post'
        db.create_table(u'djangocms_blog_post', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[user_orm_label])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('date_published', self.gf('django.db.models.fields.DateTimeField')(default=timezone.now)),
            ('date_published_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('publish', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('main_image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'], null=True, blank=True)),
            ('main_image_thumbnail', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blog_post_thumbnail', null=True, to=orm[thumbnail_model])),
            ('main_image_full', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blog_post_full', null=True, to=orm[thumbnail_model])),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Placeholder'], null=True)),
        ))
        db.send_create_signal(u'djangocms_blog', ['Post'])

        # Adding M2M table for field categories on 'Post'
        m2m_table_name = db.shorten_name(u'djangocms_blog_post_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm[u'djangocms_blog.post'], null=False)),
            ('blogcategory', models.ForeignKey(orm[u'djangocms_blog.blogcategory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['post_id', 'blogcategory_id'])

        # Adding model 'LatestPostsPlugin'
        db.create_table(u'cmsplugin_latestpostsplugin', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('latest_posts', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal(u'djangocms_blog', ['LatestPostsPlugin'])

        # Adding M2M table for field tags on 'LatestPostsPlugin'
        m2m_table_name = db.shorten_name(u'djangocms_blog_latestpostsplugin_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('latestpostsplugin', models.ForeignKey(orm[u'djangocms_blog.latestpostsplugin'], null=False)),
            ('tag', models.ForeignKey(orm[u'taggit.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['latestpostsplugin_id', 'tag_id'])

        # Adding M2M table for field categories on 'LatestPostsPlugin'
        m2m_table_name = db.shorten_name(u'djangocms_blog_latestpostsplugin_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('latestpostsplugin', models.ForeignKey(orm[u'djangocms_blog.latestpostsplugin'], null=False)),
            ('blogcategory', models.ForeignKey(orm[u'djangocms_blog.blogcategory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['latestpostsplugin_id', 'blogcategory_id'])

        # Adding model 'AuthorEntriesPlugin'
        db.create_table(u'cmsplugin_authorentriesplugin', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('latest_posts', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal(u'djangocms_blog', ['AuthorEntriesPlugin'])

        # Adding M2M table for field authors on 'AuthorEntriesPlugin'
        m2m_table_name = db.shorten_name(u'djangocms_blog_authorentriesplugin_authors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('authorentriesplugin', models.ForeignKey(orm[u'djangocms_blog.authorentriesplugin'], null=False)),
            ('user', models.ForeignKey(orm[user_orm_label], null=False))
        ))
        db.create_unique(m2m_table_name, ['authorentriesplugin_id', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'PostTranslation', fields ['language_code', 'master']
        db.delete_unique(u'djangocms_blog_post_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'PostTranslation', fields ['language_code', 'slug']
        db.delete_unique(u'djangocms_blog_post_translation', ['language_code', 'slug'])

        # Removing unique constraint on 'BlogCategoryTranslation', fields ['language_code', 'master']
        db.delete_unique(u'djangocms_blog_blogcategory_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'BlogCategoryTranslation', fields ['language_code', 'slug']
        db.delete_unique(u'djangocms_blog_blogcategory_translation', ['language_code', 'slug'])

        # Deleting model 'BlogCategoryTranslation'
        db.delete_table(u'djangocms_blog_blogcategory_translation')

        # Deleting model 'BlogCategory'
        db.delete_table(u'djangocms_blog_blogcategory')

        # Deleting model 'PostTranslation'
        db.delete_table(u'djangocms_blog_post_translation')

        # Deleting model 'Post'
        db.delete_table(u'djangocms_blog_post')

        # Removing M2M table for field categories on 'Post'
        db.delete_table(db.shorten_name(u'djangocms_blog_post_categories'))

        # Deleting model 'LatestPostsPlugin'
        db.delete_table(u'cmsplugin_latestpostsplugin')

        # Removing M2M table for field tags on 'LatestPostsPlugin'
        db.delete_table(db.shorten_name(u'djangocms_blog_latestpostsplugin_tags'))

        # Removing M2M table for field categories on 'LatestPostsPlugin'
        db.delete_table(db.shorten_name(u'djangocms_blog_latestpostsplugin_categories'))

        # Deleting model 'AuthorEntriesPlugin'
        db.delete_table(u'cmsplugin_authorentriesplugin')

        # Removing M2M table for field authors on 'AuthorEntriesPlugin'
        db.delete_table(db.shorten_name(u'djangocms_blog_authorentriesplugin_authors'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        user_model_label: {
            'Meta': {'object_name': User.__name__, 'db_table': "'%s'" % User._meta.db_table},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'djangocms_blog.authorentriesplugin': {
            'Meta': {'object_name': 'AuthorEntriesPlugin', 'db_table': "u'cmsplugin_authorentriesplugin'", '_ormbases': ['cms.CMSPlugin']},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['%s']" % user_orm_label, 'symmetrical': 'False'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        u'djangocms_blog.blogcategory': {
            'Meta': {'object_name': 'BlogCategory'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djangocms_blog.BlogCategory']", 'null': 'True', 'blank': 'True'})
        },
        u'djangocms_blog.blogcategorytranslation': {
            'Meta': {'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]", 'object_name': 'BlogCategoryTranslation', 'db_table': "u'djangocms_blog_blogcategory_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['djangocms_blog.BlogCategory']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'djangocms_blog.latestpostsplugin': {
            'Meta': {'object_name': 'LatestPostsPlugin', 'db_table': "u'cmsplugin_latestpostsplugin'", '_ormbases': ['cms.CMSPlugin']},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['djangocms_blog.BlogCategory']", 'symmetrical': 'False', 'blank': 'True'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'latest_posts': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['taggit.Tag']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'djangocms_blog.post': {
            'Meta': {'ordering': "('-date_published', '-date_created')", 'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s']" % user_orm_label}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'blog_posts'", 'symmetrical': 'False', 'to': u"orm['djangocms_blog.BlogCategory']"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_published_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            'main_image_full': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blog_post_full'", 'null': 'True', 'to': u"orm['%s']" % thumbnail_model}),
            'main_image_thumbnail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blog_post_thumbnail'", 'null': 'True', 'to': u"orm['%s']" % thumbnail_model}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'djangocms_blog.posttranslation': {
            'Meta': {'unique_together': "[('language_code', 'slug'), ('language_code', 'master')]", 'object_name': 'PostTranslation', 'db_table': "u'djangocms_blog_post_translation'"},
            'abstract': ('djangocms_text_ckeditor.fields.HTMLField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['djangocms_blog.Post']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_files'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_files'", 'null': 'True', 'to': u"orm['%s']" % user_orm_label}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_filer.file_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.folder': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('parent', 'name'),)", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filer_owned_folders'", 'null': 'True', 'to': u"orm['%s']" % user_orm_label}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.image': {
            'Meta': {'object_name': 'Image', '_ormbases': ['filer.File']},
            '_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['filer.File']", 'unique': 'True', 'primary_key': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'related_url': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['djangocms_blog']
