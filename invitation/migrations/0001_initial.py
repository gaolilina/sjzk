# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-07 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(db_index=True, max_length=100, verbose_name='附带消息')),
                ('create_time', models.DateTimeField(db_index=True, verbose_name='邀请时间')),
                ('is_read', models.BooleanField(db_index=True, default=False, verbose_name='该邀请是否已读')),
                ('is_ignored', models.BooleanField(db_index=True, default=False, verbose_name='该邀请是否已被忽略')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', related_query_name='invitation', to='team.Team', verbose_name='邀请方团队')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', related_query_name='invitation', to='user.User', verbose_name='被邀请用户')),
            ],
            options={
                'db_table': 'team_invitation',
                'ordering': ['-create_time'],
            },
        ),
    ]
