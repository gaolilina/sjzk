#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Auto generated by activity.py
import json

from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import *
from main.models.activity import *


class ActivityView(View):
    @fetch_record(Activity.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("activity/activity.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @require_cookie
    @require_role('xyz')
    @validate_args2({
        'name': forms.CharField(max_length=50, required=False),
        'tags': forms.CharField(max_length=50, required=False),
        'content': forms.CharField(max_length=1000, required=False),
        'deadline': forms.DateTimeField(required=False),
        'time_started': forms.DateTimeField(required=False),
        'time_ended': forms.DateTimeField(required=False),
        'allow_user': forms.IntegerField(),
        'type': forms.IntegerField(required=False),
        'status': forms.IntegerField(required=False),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'user_type': forms.IntegerField(required=False),
        'stages': forms.CharField(required=False),
        'achievement': forms.CharField(required=False),
    })
    @fetch_record(Activity.enabled, 'model', 'id')
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]
        if model.state == Activity.STATE_PASSED \
                or 'type' in kwargs and kwargs['type'] not in Activity.TYPES:
            return HttpResponseForbidden()

        for k in kwargs:
            if k != "stages":
                setattr(model, k, kwargs[k])
        # 如果已被拒绝，则重新填写资料会被放入审核中状态
        if model.state == Activity.STATE_NO:
            model.state = Activity.STATE_CHECKING
        model.save()

        if 'stages' in kwargs and kwargs['stages'] != "":
            ActivityStage.objects.filter(activity=model).delete()

            stages = json.loads(kwargs['stages'])
            for st in stages:
                model.stages.create(status=int(st['status']), time_started=st['time_started'],
                                    time_ended=st['time_ended'])

        template = loader.get_template("admin_activity/edit.html")
        context = Context({'model': model, 'msg': '保存成功', 'user': request.user,
                           'stages': ActivityStage.objects.filter(activity=model)})
        return HttpResponse(template.render(context))


class ActivityList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = Activity.objects.filter(activity_id=kwargs["id"])
            template = loader.get_template("activity/activity_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:activity:activity', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("activity/index.html")
            if Activity == Activity:
                redir = 'admin:activity:activity'
            else:
                redir = 'admin:activity:activity_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Activity.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'activity', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("activity/index.html")
            context = Context({'rb': 'activity', 'user': request.user})
            return HttpResponse(template.render(context))


class ActivityCommentView(View):
    @fetch_record(ActivityComment.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("activity/activity_comment.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(ActivityComment.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'content': forms.CharField(max_length=100, ), 'time_created': forms.DateTimeField(required=False, ),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("activity_comment", mod.id, 1, request.user)

        template = loader.get_template("activity/activity_comment.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class ActivityCommentList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = ActivityComment.objects.filter(entity_id=kwargs["id"])
            template = loader.get_template("activity/activity_comment_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:activity:activity_comment', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("activity/index.html")
            if ActivityComment == Activity:
                redir = 'admin:activity:activity'
            else:
                redir = 'admin:activity:activity_comment_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Activity.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'activity_comment', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("activity/index.html")
            context = Context({'rb': 'activity_comment', 'user': request.user})
            return HttpResponse(template.render(context))


class ActivityLikerView(View):
    @fetch_record(ActivityLiker.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("activity/activity_liker.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(ActivityLiker.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'time_created': forms.DateTimeField(required=False, ),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("activity_liker", mod.id, 1, request.user)

        template = loader.get_template("activity/activity_liker.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class ActivityLikerList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = ActivityLiker.objects.filter(activity_id=kwargs["id"])
            template = loader.get_template("activity/activity_liker_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:activity:activity_liker', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("activity/index.html")
            if ActivityLiker == Activity:
                redir = 'admin:activity:activity'
            else:
                redir = 'admin:activity:activity_liker_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Activity.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'activity_liker', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("activity/index.html")
            context = Context({'rb': 'activity_liker', 'user': request.user})
            return HttpResponse(template.render(context))


class ActivityStageView(View):
    @fetch_record(ActivityStage.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("activity/activity_stage.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(ActivityStage.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'status': forms.IntegerField(required=False, ), 'time_started': forms.DateTimeField(required=False, ),
        'time_ended': forms.DateTimeField(required=False, ), 'time_created': forms.DateTimeField(required=False, ),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("activity_stage", mod.id, 1, request.user)

        template = loader.get_template("activity/activity_stage.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class ActivityStageList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = ActivityStage.objects.filter(activity_id=kwargs["id"])
            template = loader.get_template("activity/activity_stage_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:activity:activity_stage', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("activity/index.html")
            if ActivityStage == Activity:
                redir = 'admin:activity:activity'
            else:
                redir = 'admin:activity:activity_stage_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Activity.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'activity_stage', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("activity/index.html")
            context = Context({'rb': 'activity_stage', 'user': request.user})
            return HttpResponse(template.render(context))


class ActivityUserParticipatorView(View):
    @fetch_record(ActivityUserParticipator.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("activity/activity_user_participator.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(ActivityUserParticipator.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'time_created': forms.DateTimeField(required=False, ),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("activity_user_participator", mod.id, 1, request.user)

        template = loader.get_template("activity/activity_user_participator.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class ActivityUserParticipatorList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = ActivityUserParticipator.objects.filter(activity_id=kwargs["id"])
            template = loader.get_template("activity/activity_user_participator_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:activity:activity_user_participator',
                               'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("activity/index.html")
            if ActivityUserParticipator == Activity:
                redir = 'admin:activity:activity'
            else:
                redir = 'admin:activity:activity_user_participator_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Activity.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'activity_user_participator', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("activity/index.html")
            context = Context({'rb': 'activity_user_participator', 'user': request.user})
            return HttpResponse(template.render(context))
