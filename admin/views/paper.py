#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from json import JSONDecodeError

from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from admin.utils.decorators import require_cookie, require_role, validate_args2
from main.utils import abort
from main.utils.decorators import fetch_object, validate_args
from modellib.models.paper.paper import Paper


class PaperList(View):

    @require_cookie
    @require_role('xyz')
    @validate_args2({
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
            papers = Paper.objects.filter(**params)[offset: offset + limit]
        else:
            papers = Paper.objects.all()[offset: offset + limit]
        return JsonResponse({
            'count': len(papers),
            'list': [{
                'id': p.id,
                'name': p.name,
                'desc': p.desc,
                'enable': p.enable,
                'count': p.count_question,
            } for p in papers]
        })

    @require_cookie
    @require_role('xyz')
    @validate_args2({
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
        return JsonResponse({})


class PaperDetail(View):

    @require_cookie
    @require_role('xyz')
    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
    })
    @fetch_object(Paper.objects, 'paper')
    def get(self, request, paper, **kwargs):
        return JsonResponse({
            'name': paper.name,
            'desc': paper.desc,
            'enable': paper.enable,
            'count': paper.count_question,
            'questions': json.loads(paper.questions),
        })

    @require_cookie
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
                    abort(400, 'questions should be list and not empty')
                paper.count_question = len(questions_list)
                paper.questions = questions
                has_update = True
            except JSONDecodeError:
                abort(400, 'questions should be json str')
        if has_update:
            paper.save()
        return JsonResponse({})


class PaperSwitch(View):

    @require_cookie
    @require_role('xyz')
    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
        'enable': forms.BooleanField(required=False)
    })
    @fetch_object(Paper.objects, 'paper')
    def post(self, request, paper, enable):
        if paper.enable != enable:
            Paper.objects.filter(id=paper.id).update(enable=enable)
        return JsonResponse({})
