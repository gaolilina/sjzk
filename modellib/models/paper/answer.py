#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class PaperAnswer(models.Model):
    class Meta:
        db_table = 'paper_answer'

    paper = models.ForeignKey('Paper', related_name='answers')
    content = models.TextField()
    user = models.ForeignKey('main.User', related_name='answers', default=None)
