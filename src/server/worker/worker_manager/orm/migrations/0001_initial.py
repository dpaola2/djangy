# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LocalApplication'
        db.create_table('local_application', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('bundle_version', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('is_stopped', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('num_procs', self.gf('django.db.models.fields.IntegerField')()),
            ('proc_num_threads', self.gf('django.db.models.fields.IntegerField')()),
            ('proc_mem_mb', self.gf('django.db.models.fields.IntegerField')()),
            ('proc_stack_mb', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('orm', ['LocalApplication'])

        # Adding model 'LocalApplicationLocks'
        db.create_table('local_application_locks', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orm.LocalApplication'], unique=True)),
            ('pid', self.gf('django.db.models.fields.IntegerField')()),
            ('time', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('orm', ['LocalApplicationLocks'])


    def backwards(self, orm):
        
        # Deleting model 'LocalApplication'
        db.delete_table('local_application')

        # Deleting model 'LocalApplicationLocks'
        db.delete_table('local_application_locks')


    models = {
        'orm.localapplication': {
            'Meta': {'object_name': 'LocalApplication', 'db_table': "'local_application'"},
            'application_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'bundle_version': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
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
