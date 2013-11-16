# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Job'
        db.create_table(u'cruncher_job', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'cruncher', ['Job'])

        # Adding model 'Payment'
        db.create_table(u'cruncher_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cruncher.Job'])),
            ('balance', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'cruncher', ['Payment'])

        # Adding model 'File'
        db.create_table(u'cruncher_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cruncher.Job'])),
        ))
        db.send_create_signal(u'cruncher', ['File'])

        # Adding model 'UserProfile'
        db.create_table(u'cruncher_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('credits', self.gf('django.db.models.fields.IntegerField')()),
            ('current_job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cruncher.Job'])),
        ))
        db.send_create_signal(u'cruncher', ['UserProfile'])


    def backwards(self, orm):
        # Deleting model 'Job'
        db.delete_table(u'cruncher_job')

        # Deleting model 'Payment'
        db.delete_table(u'cruncher_payment')

        # Deleting model 'File'
        db.delete_table(u'cruncher_file')

        # Deleting model 'UserProfile'
        db.delete_table(u'cruncher_userprofile')


    models = {
        u'cruncher.file': {
            'Meta': {'object_name': 'File'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cruncher.Job']"}),
            'path': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'cruncher.job': {
            'Meta': {'object_name': 'Job'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        u'cruncher.payment': {
            'Meta': {'object_name': 'Payment'},
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cruncher.Job']"}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'cruncher.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'credits': ('django.db.models.fields.IntegerField', [], {}),
            'current_job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cruncher.Job']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['cruncher']