# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Application.max_processes'
        db.delete_column('application', 'max_processes')

        # Adding field 'Application.proc_num_threads'
        db.add_column('application', 'proc_num_threads', self.gf('django.db.models.fields.IntegerField')(default=5), keep_default=False)

        # Adding field 'Application.proc_mem_mb'
        db.add_column('application', 'proc_mem_mb', self.gf('django.db.models.fields.IntegerField')(default=64), keep_default=False)

        # Adding field 'Application.proc_stack_mb'
        db.add_column('application', 'proc_stack_mb', self.gf('django.db.models.fields.IntegerField')(default=2), keep_default=False)

        # Adding field 'Application.debug'
        db.add_column('application', 'debug', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Process.num_procs'
        db.add_column('process', 'num_procs', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding unique constraint on 'Process', fields ['application', 'host']
        db.create_unique('process', ['application_id', 'host'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Process', fields ['application', 'host']
        db.delete_unique('process', ['application_id', 'host'])

        # Adding field 'Application.max_processes'
        db.add_column('application', 'max_processes', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Deleting field 'Application.proc_num_threads'
        db.delete_column('application', 'proc_num_threads')

        # Deleting field 'Application.proc_mem_mb'
        db.delete_column('application', 'proc_mem_mb')

        # Deleting field 'Application.proc_stack_mb'
        db.delete_column('application', 'proc_stack_mb')

        # Deleting field 'Application.debug'
        db.delete_column('application', 'debug')

        # Deleting field 'Process.num_procs'
        db.delete_column('process', 'num_procs')


    models = {
        'management_database.application': {
            'Meta': {'object_name': 'Application', 'db_table': "'application'"},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['management_database.User']"}),
            'app_gid': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'bundle_version': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'cron_uid': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'db_host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_max_size_mb': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'db_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_port': ('django.db.models.fields.IntegerField', [], {'default': '3306'}),
            'db_username': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'debug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'proc_mem_mb': ('django.db.models.fields.IntegerField', [], {'default': '64'}),
            'proc_num_threads': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'proc_stack_mb': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'setup_uid': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'web_uid': ('django.db.models.fields.IntegerField', [], {'default': '-1'})
        },
        'management_database.process': {
            'Meta': {'unique_together': "(('application', 'host'),)", 'object_name': 'Process', 'db_table': "'process'"},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['management_database.Application']"}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_procs': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'management_database.user': {
            'Meta': {'object_name': 'User', 'db_table': "'user'"},
            'admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'passwd': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'management_database.whitelist': {
            'Meta': {'object_name': 'WhiteList', 'db_table': "'whitelist'"},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_code': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['management_database']
