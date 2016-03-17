# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-15 11:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('team', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamNeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(db_index=True, max_length=100, verbose_name='需求描述')),
                ('status', models.IntegerField(choices=[('未满足', 0), ('已满足', 1)], default=0, verbose_name='状态')),
                ('create_time', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='创建时间')),
                ('number', models.IntegerField(db_index=True, default=-1, verbose_name='需求人数')),
                ('gender', models.IntegerField(choices=[('不限', 0), ('男', 1), ('女', 2)], default=0, verbose_name='性别要求')),
                ('city', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='location.City', verbose_name='地区要求（市级）')),
                ('province', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='location.Province', verbose_name='地区要求（省级）')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='needs', related_query_name='need', to='team.Team')),
            ],
            options={
                'db_table': 'team_need',
                'ordering': ['-create_time'],
            },
        ),
    ]
