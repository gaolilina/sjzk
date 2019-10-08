from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Competition, User
from main.utils import abort
from util.decorator.auth import admin_auth, cms_auth
from util.decorator.param import fetch_object, validate_args


class CompetitionExpertList(View):
    @fetch_object(Competition.enabled, 'competition')
    @admin_auth
    @validate_args({
        'api': forms.IntegerField(required=False),
    })
    def get(self, request, competition, api=0):
        if api == 1:
            c = competition.experts.all().count()
            qs = competition.experts.all()
            l = [{'id': user.id,
                  'time_created': user.time_created,
                  'name': user.name,
                  'icon_url': user.icon,
                  'description': user.description,
                  'email': user.email,
                  'gender': user.gender,
                  'birthday': user.birthday,
                  'province': user.province,
                  'city': user.city,
                  'county': user.county,
                  'follower_count': user.followers.count(),
                  'followed_count': user.followed_users.count() + user.followed_teams.count(),
                  'friend_count': user.friends.count(),
                  'liker_count': user.likers.count(),
                  'visitor_count': user.visitors.count(),
                  'is_verified': user.is_verified,
                  'is_role_verified': user.is_role_verified,
                  'role': user.role,
                  'adept_field': user.adept_field,
                  'adept_skill': user.adept_skill,
                  'expect_role': user.expect_role,
                  'follow_field': user.follow_field,
                  'follow_skill': user.follow_skill,
                  'unit1': user.unit1,
                  'unit2': user.unit2,
                  'profession': user.profession,
                  'score': user.score} for user in qs]
            return JsonResponse({'count': c, 'list': l})
        template = loader.get_template("admin_competition/add_expert.html")
        context = Context({
            'model': competition,
            'user': request.user,
            'experts': competition.experts.all(),
            'all_experts': User.enabled.filter(role='专家').all(),
            'participators': competition.team_participators.all(),
        })
        return HttpResponse(template.render(context))

    @cms_auth
    @fetch_object(Competition.enabled, 'competition')
    @validate_args({
        'expert_id': forms.IntegerField(),
    })
    def post(self, request, competition, expert_id):
        expert = User.objects.filter(pk=expert_id).get()
        competition.experts.add(expert)
        abort(200)


class CompetitionTeamList(View):
    @fetch_object(Competition.enabled, 'competition')
    @admin_auth
    @validate_args({
        'final': forms.BooleanField(required=False),
    })
    def get(self, request, competition, final=False):
        template = loader.get_template("admin_competition/promote_team.html")
        c = CompetitionTeamParticipator.objects.filter(competition=competition, final=final).all().count()
        qs = CompetitionTeamParticipator.objects.filter(competition=competition, final=final).all()
        context = Context({
            'teams': qs,
        })
        return HttpResponse(template.render(context))
        # l = [{'id': user.id,
        #     'score': user.score,
        #     'rater': user.rater.id,
        #     'final': user.final} for user in qs]
        # return JsonResponse({'count': c, 'list': l})


# Auto generated by competition.py
from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from main.models.competition import *

from admin.utils.decorators import *
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args


class CompetitionCommentView(View):
    @fetch_record(CompetitionComment.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_comment.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionComment.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'content': forms.CharField(max_length=100, ), 'time_created': forms.DateTimeField(required=False, ),
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
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionComment.objects.filter(entity_id=kwargs["id"])
            template = loader.get_template("competition/competition_comment_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:competition:competition_comment', 'user': request.user})
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
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_file.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionFile.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'status': forms.IntegerField(required=False, ), 'file': forms.CharField(max_length=100, required=False, ),
        'time_created': forms.DateTimeField(required=False, ),
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
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionFile.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_file_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:competition:competition_file', 'user': request.user})
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
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_liker.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionLiker.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'time_created': forms.DateTimeField(required=False, ),
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
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionLiker.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_liker_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:competition:competition_liker', 'user': request.user})
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
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_notification.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionNotification.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'status': forms.IntegerField(required=False, ), 'notification': forms.CharField(max_length=1000, ),
        'time_created': forms.DateTimeField(required=False, ),
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
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionNotification.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_notification_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_notification',
                               'user': request.user})
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
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_stage.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionStage.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'status': forms.IntegerField(required=False, ), 'time_started': forms.DateTimeField(required=False, ),
        'time_ended': forms.DateTimeField(required=False, ), 'time_created': forms.DateTimeField(required=False, ),
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
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionStage.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_stage_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:competition:competition_stage', 'user': request.user})
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
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition_team_participator.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(CompetitionTeamParticipator.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'time_created': forms.DateTimeField(required=False, ),
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
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = CompetitionTeamParticipator.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_team_participator_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:competition:competition_team_participator',
                               'user': request.user})
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
