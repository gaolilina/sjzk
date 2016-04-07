# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-07 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=20, verbose_name='名称')),
                ('description', models.TextField(db_index=True, max_length=100, verbose_name='简介')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='是否有效')),
                ('managers', models.ManyToManyField(db_table='team_manager', related_name='managed_teams', related_query_name='managed_team', to='user.User', verbose_name='管理员')),
            ],
            options={
                'db_table': 'team',
            },
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('join_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='加入时间')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='user.User', verbose_name='成员')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership', to='team.Team', verbose_name='团队')),
            ],
            options={
                'db_table': 'team_member',
            },
        ),
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(related_name='teams', related_query_name='team', through='team.TeamMembership', to='user.User', verbose_name='成员'),
        ),
        migrations.AddField(
            model_name='team',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_teams', related_query_name='owned_team', to='user.User', verbose_name='创始人'),
        ),
    ]
