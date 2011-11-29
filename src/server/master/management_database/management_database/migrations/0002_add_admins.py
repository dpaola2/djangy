# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.core.management import call_command

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # outdated


    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'management_database.application': {
            'Meta': {'object_name': 'Application', 'db_table': "'application'"},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['management_database.User']"}),
            'cron_uid': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'db_host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_max_size_mb': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'db_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_port': ('django.db.models.fields.IntegerField', [], {'default': '3306'}),
            'db_username': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_processes': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'setup_uid': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'web_uid': ('django.db.models.fields.IntegerField', [], {'default': '-1'})
        },
        'management_database.process': {
            'Meta': {'object_name': 'Process', 'db_table': "'process'"},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['management_database.Application']"}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
