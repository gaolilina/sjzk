#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from json import JSONDecodeError

from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.utils import abort
from main.utils.decorators import validate_args, fetch_object, require_token
from modellib.models.paper import Paper, PaperAnswer


class PaperDetail(View):

    @require_token
    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
    })
    @fetch_object(Paper.objects, 'paper')
    def get(self, request, paper, **kwargs):
        return JsonResponse({
            'id': paper.id,
            'name': paper.name,
            'desc': paper.desc,
            'enable': paper.enable,
            'count': paper.count_question,
            'questions': json.loads(paper.questions),
        })


class AnswerThePaper(View):

    @require_token
    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
        'answers': forms.CharField(max_length=1000),
    })
    @fetch_object(Paper.objects, 'paper')
    def post(self, request, paper, answers):
        if paper.answers.filter(user=request.user).count() != 0:
            abort(403, "you have answer the question")
        try:
            answer_list = json.loads(answers)
            if not isinstance(answer_list, list) or len(answer_list) != paper.count_question:
                abort(400, 'answer should be list and equal question count')
        except JSONDecodeError:
            abort(400, 'answer should be json str')
        PaperAnswer.objects.create(paper=paper, content=answers, user=request.user)
        return JsonResponse({})
