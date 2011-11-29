# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'LocalApplication.celery_procs'
        db.add_column('local_application', 'celery_procs', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'LocalApplication.celery_procs'
        db.delete_column('local_application', 'celery_procs')


    models = {
        'orm.localapplication': {
            'Meta': {'object_name': 'LocalApplication', 'db_table': "'local_application'"},
            'application_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'bundle_version': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'celery_procs': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_stopped': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'num_procs': ('django.db.models.fields.IntegerField', [], {}),
            'proc_mem_mb': ('django.db.models.fields.IntegerField', [], {}),
            'proc_num_threads': ('django.db.models.fields.IntegerField', [], {}),
            'proc_stack_mb': ('django.db.models.fields.IntegerField', [], {})
        },
        'orm.localapplicationlocks': {
            'Meta': {'object_name': 'LocalApplicationLocks', 'db_table': "'local_application_locks'"},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['orm.LocalApplication']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.IntegerField', [], {}),
            'time': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['orm']
