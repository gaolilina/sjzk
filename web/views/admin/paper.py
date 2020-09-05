#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from json import JSONDecodeError

from django import forms
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.template import loader, Context
from django.views.generic.base import View

from admin.utils.decorators import require_role
from util.decorator.auth import admin_auth, cms_auth
from main.utils import abort
from util.decorator.param import fetch_object, validate_args, old_validate_args
from modellib.models.paper.paper import Paper
from util.base.view import BaseView


class PaperAdd(BaseView):

    @admin_auth
    @require_role('xyz')
    def get(self, request):
        context = Context({
            'user': request.user,
        })
        return self.success(data=context)

    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'name': forms.CharField(max_length=50),
        'desc': forms.CharField(max_length=250, required=False),
        'questions': forms.CharField(max_length=1000),
    })
    def post(self, request, name, questions, desc='', **kwargs):
        try:
            questions_list = json.loads(questions)
            if not isinstance(questions_list, list) or len(questions_list) == 0:
                abort(400, 'questions should be list and not empty')
        except JSONDecodeError:
            abort(400, 'questions should be json str')
        Paper.objects.create(
            name=name,
            desc=desc,
            count_question=len(questions_list),
            questions=questions
        )
        context = Context({
            'user': request.user,
        })
        return self.success(data=context)


class PaperList(BaseView):

    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(max_length=50, required=False),
        'enable': forms.NullBooleanField(required=False)
    })
    def get(self, request, name=None, enable=None, offset=0, limit=10, **kwargs):
        """
        调查问卷列表，提供查询，名字和是否启用
        :return:
        """
        params = {}
        if name is not None:
            params['name__contains'] = name
        if enable is not None:
            params['enable'] = enable
        if len(params) != 0:
            papers = Paper.objects.filter(**params)
        else:
            papers = Paper.objects.all()
        context = Context({
            'user': request.user,
            'list': papers
        })
        return self.success(data=context)


class PaperDetail(BaseView):

    @admin_auth
    @require_role('xyz')
    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
    })
    @fetch_object(Paper.objects, 'paper')
    def get(self, request, paper, **kwargs):
        paper.questions = json.loads(paper.questions)
        context = Context({
            'user': request.user,
            'model': paper
        })
        return self.success(data=context)

    @admin_auth
    @require_role('xyz')
    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
        'name': forms.CharField(max_length=50, required=False),
        'desc': forms.CharField(max_length=250, required=False),
        'questions': forms.CharField(max_length=1000, required=False),
    })
    @fetch_object(Paper.objects, 'paper')
    def post(self, request, paper, **kwargs):
        update_list = ['name', 'desc']
        has_update = False
        for p in update_list:
            if p in kwargs:
                setattr(paper, p, kwargs[p])
                has_update = True
        if 'questions' in kwargs:
            questions = kwargs['questions']
            try:
                questions_list = json.loads(questions)
                if not isinstance(questions_list, list) or len(questions_list) == 0:
                    return HttpResponseBadRequest()
                paper.count_question = len(questions_list)
                paper.questions = questions
                has_update = True
            except JSONDecodeError:
                return HttpResponseBadRequest()
        if has_update:
            paper.save()
        paper.questions = json.loads(paper.questions)
        context = Context({
            'user': request.user,
            'model': paper
        })
        return self.success(data=context)


class PaperSwitch(BaseView):

    @cms_auth
    @require_role('xyz')
    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
        'enable': forms.BooleanField(required=False)
    })
    @fetch_object(Paper.objects, 'paper')
    def post(self, request, paper, enable):
        if paper.enable != enable:
            Paper.objects.filter(id=paper.id).update(enable=enable)
        return self.success()
