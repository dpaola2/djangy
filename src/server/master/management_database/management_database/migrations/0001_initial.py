# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WhiteList'
        db.create_table('whitelist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('invite_code', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('management_database', ['WhiteList'])

        # Adding model 'User'
        db.create_table('user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('passwd', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('management_database', ['User'])

        # Adding model 'Application'
        db.create_table('application', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management_database.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('max_processes', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('db_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('db_username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('db_password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('db_host', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('db_port', self.gf('django.db.models.fields.IntegerField')(default=3306)),
            ('db_max_size_mb', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('setup_uid', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('web_uid', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('cron_uid', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal('management_database', ['Application'])

        # Adding model 'Process'
        db.create_table('process', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management_database.Application'])),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('management_database', ['Process'])


    def backwards(self, orm):
        
        # Deleting model 'WhiteList'
        db.delete_table('whitelist')

        # Deleting model 'User'
        db.delete_table('user')

        # Deleting model 'Application'
        db.delete_table('application')

        # Deleting model 'Process'
        db.delete_table('process')


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
