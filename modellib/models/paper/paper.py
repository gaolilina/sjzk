#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models


class Paper(models.Model):
    class Meta:
        db_table = 'paper'

    name = models.CharField(max_length=100)
    desc = models.TextField()
    enable = models.BooleanField(default=True)
    count_question = models.IntegerField()
    questions = models.TextField()
