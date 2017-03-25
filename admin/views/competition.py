# Auto generated by competition.py
from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from main.models.competition import *

from admin.utils.decorators import *
class CompetitionView(View):
    @fetch_record(Competition.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(Competition.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'name': forms.CharField(max_length=50,),'status': forms.IntegerField(required=False,),'content': forms.CharField(max_length=1000,),'deadline': forms.DateTimeField(required=False,),'time_started': forms.DateTimeField(required=False,),'time_ended': forms.DateTimeField(required=False,),'time_created': forms.DateTimeField(required=False,),'allow_team': forms.IntegerField(required=False,),'province': forms.CharField(max_length=20,required=False,),'city': forms.CharField(max_length=20,required=False,),'min_member': forms.IntegerField(required=False,),'max_member': forms.IntegerField(required=False,),'unit': forms.CharField(max_length=20,required=False,),'user_type': forms.IntegerField(required=False,),'is_enabled': forms.BooleanField(required=False),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition", mod.id, 1, request.user)

        template = loader.get_template("competition/competition.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class CompetitionList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = Competition.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if Competition == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition', 'user': request.user})
            return HttpResponse(template.render(context))
class CompetitionCommentView(View):
    @fetch_record(CompetitionComment.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_comment.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionComment.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'content': forms.CharField(max_length=100,),'time_created': forms.DateTimeField(required=False,),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition_comment", mod.id, 1, request.user)

        template = loader.get_template("competition/competition_comment.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class CompetitionCommentList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionComment.objects.filter(entity_id=kwargs["id"])
            template = loader.get_template("competition/competition_comment_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_comment', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if CompetitionComment == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_comment_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition_comment', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition_comment', 'user': request.user})
            return HttpResponse(template.render(context))
class CompetitionFileView(View):
    @fetch_record(CompetitionFile.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_file.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionFile.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'status': forms.IntegerField(required=False,),'file': forms.CharField(max_length=100,required=False,),'time_created': forms.DateTimeField(required=False,),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition_file", mod.id, 1, request.user)

        template = loader.get_template("competition/competition_file.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class CompetitionFileList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionFile.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_file_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_file', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if CompetitionFile == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_file_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition_file', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition_file', 'user': request.user})
            return HttpResponse(template.render(context))
class CompetitionLikerView(View):
    @fetch_record(CompetitionLiker.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_liker.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionLiker.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'time_created': forms.DateTimeField(required=False,),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition_liker", mod.id, 1, request.user)

        template = loader.get_template("competition/competition_liker.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class CompetitionLikerList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionLiker.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_liker_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_liker', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if CompetitionLiker == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_liker_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition_liker', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition_liker', 'user': request.user})
            return HttpResponse(template.render(context))
class CompetitionNotificationView(View):
    @fetch_record(CompetitionNotification.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_notification.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionNotification.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'status': forms.IntegerField(required=False,),'notification': forms.CharField(max_length=1000,),'time_created': forms.DateTimeField(required=False,),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition_notification", mod.id, 1, request.user)

        template = loader.get_template("competition/competition_notification.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class CompetitionNotificationList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionNotification.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_notification_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_notification', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if CompetitionNotification == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_notification_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition_notification', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition_notification', 'user': request.user})
            return HttpResponse(template.render(context))
class CompetitionStageView(View):
    @fetch_record(CompetitionStage.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_stage.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionStage.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'status': forms.IntegerField(required=False,),'time_started': forms.DateTimeField(required=False,),'time_ended': forms.DateTimeField(required=False,),'time_created': forms.DateTimeField(required=False,),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition_stage", mod.id, 1, request.user)

        template = loader.get_template("competition/competition_stage.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class CompetitionStageList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionStage.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_stage_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_stage', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if CompetitionStage == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_stage_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition_stage', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition_stage', 'user': request.user})
            return HttpResponse(template.render(context))
class CompetitionTeamParticipatorView(View):
    @fetch_record(CompetitionTeamParticipator.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_team_participator.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionTeamParticipator.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'time_created': forms.DateTimeField(required=False,),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition_team_participator", mod.id, 1, request.user)

        template = loader.get_template("competition/competition_team_participator.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class CompetitionTeamParticipatorList(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionTeamParticipator.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_team_participator_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_team_participator', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if CompetitionTeamParticipator == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_team_participator_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition_team_participator', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition_team_participator', 'user': request.user})
            return HttpResponse(template.render(context))
