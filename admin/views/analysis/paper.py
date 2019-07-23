#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from modellib.models.paper import Paper
from util.decorator.param import fetch_object, validate_args


class PaperAnalysis(View):
    KEY_ANALYSIS = 'analysis'

    @validate_args({
        'paper_id': forms.IntegerField(min_value=0),
        'date_start': forms.DateField(required=False),
        'date_end': forms.DateField(required=False),
    })
    @fetch_object(Paper.objects, 'paper')
    def get(self, request, paper, date_start=None, date_end=None, **kwargs):
        # 筛选答案
        condititon = {}
        if date_start is not None:
            condititon['time_created__gte'] = date_start
        if date_end is not None:
            condititon['time_created__lt'] = date_end
        count_answer = paper.answers.filter(**condititon).count()

        # 分析
        questions = json.loads(paper.questions)
        self.__init_analysis_result(questions)
        if count_answer > 0:
            answers = paper.answers.filter(**condititon)
            for a in answers:
                print(a.time_created)
                self.__analysis_an_answer(questions, json.loads(a.content))
        return JsonResponse({
            'sum': count_answer,
            'result': questions,
        })

    def __init_analysis_result(self, questions):
        '''
        初始化分析结果
        在原始问题结构上添加一个 analysis 字段，作为分析的结果
        {
            title:String,
            type:Int,
            option:List
            analysis: Analysis
        }

        Analysis 结构如下
        {
            count:List, // 统计，单选和多选题使用该字段，统计各个选项的结果
            origin:List, // 原始结果，目前问答题使用该字段，将原始结果直接放入 list
        }
        :return:
        '''
        key = PaperAnalysis.KEY_ANALYSIS
        key_option = 'options'
        for q in questions:
            q[key] = {
                'count': [0] * len(q[key_option]),
                'origin': list(),
            }

    def __analysis_an_answer(self, questions, answers):
        key = PaperAnalysis.KEY_ANALYSIS
        for i in range(len(questions)):
            q = questions[i]
            a = answers[i]

            # 单选题
            if q['type'] == 1:
                q[key]['count'][a] += 1
            # 多选题
            elif q['type'] == 2:
                for item in a:
                    q[key]['count'][item] += 1
            elif q['type'] == 0:
                q[key]['origin'].append(a)
