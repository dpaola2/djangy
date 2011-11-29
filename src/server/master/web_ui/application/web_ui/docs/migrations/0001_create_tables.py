# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Page'
        db.create_table('docs_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('rendered', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('docs', ['Page'])


    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('docs_page')


    models = {
        'docs.page': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'rendered': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['docs']
