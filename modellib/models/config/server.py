#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class ServerConfig(models.Model):
    class Meta:
        db_table = 'config_server'

    # 环信 access_token
    huanxin_token = models.CharField(max_length=200, default='')
