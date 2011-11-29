# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'User.customer_id'
        db.add_column('user', 'customer_id', self.gf('django.db.models.fields.CharField')(default=-1, max_length=255), keep_default=False)

        # Adding field 'User.subscription_id'
        db.add_column('user', 'subscription_id', self.gf('django.db.models.fields.CharField')(default=-1, max_length=255), keep_default=False)

        # Adding field 'User.masked_cc'
        db.add_column('user', 'masked_cc', self.gf('django.db.models.fields.CharField')(default=-1, max_length=255), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'User.customer_id'
        db.delete_column('user', 'customer_id')

        # Deleting field 'User.subscription_id'
        db.delete_column('user', 'subscription_id')

        # Deleting field 'User.masked_cc'
        db.delete_column('user', 'masked_cc')


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
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'customer_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'masked_cc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'passwd': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subscription_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'management_database.whitelist': {
            'Meta': {'object_name': 'WhiteList', 'db_table': "'whitelist'"},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_code': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['management_database']
