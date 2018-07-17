from django import forms
from django.http import JsonResponse
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist

from ..models import Competition, Team, CompetitionFile as File, CompetitionTeamParticipator
from ..utils import abort, save_uploaded_file
from ..utils.decorators import *


__all__ = ['List', 'Detail', 'CompetitionStageList', 'CompetitionFile', 'CompetitionFileScore',
           'CompetitionFileList', 'TeamParticipatorList', 'Search', 'Screen',
           'CompetitionNotification', 'CompetitionAwardList', 'CompetitionFileExpert',
           'CompetitionExpertList', 'CompetitionTeamScore']


class List(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'history': forms.BooleanField(required=False),
    })
    def get(self, request, offset=0, limit=10, order=1, history=False):
        """获取竞赛列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param history: 是否往期活动（默认否）

        :return:
            count: 竞赛总数
            list: 竞赛列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
                province:
        """

        k = self.ORDERS[order]
        if history is False:
            c = Competition.enabled.exclude(status=6).count()
            qs = Competition.enabled.exclude(
                status=6).order_by(k)[offset: offset + limit]
        else:
            c = Competition.enabled.filter(status=6).count()
            qs = Competition.enabled.filter(
                status=6).order_by(k)[offset: offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'status': a.status,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created,
              'province': a.province} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class Detail(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    def get(self, request, competition):
        """获取竞赛详情
        :return:
            id: 竞赛ID
            name: 竞赛名
            liker_count: 点赞数
            time_started: 开始时间
            time_ended: 结束时间
            deadline: 截止时间
            allow_team: 允许报名团队数
            team_participator_count: 已报名数
            status: 竞赛当前阶段
            province: 省
            city: 城市
            unit: 机构
            user_type: 参与人员身份
            time_created: 创建时间
        """

        return JsonResponse({
            'id': competition.id,
            'name': competition.name,
            'content': competition.content,
            'liker_count': competition.likers.count(),
            'time_started': competition.time_started,
            'time_ended': competition.time_ended,
            'deadline': competition.deadline,
            'allow_team': competition.allow_team,
            'team_participator_count': competition.team_participators.count(),
            'status': competition.status,
            'province': competition.province,
            'city': competition.city,
            'unit': competition.unit,
            'user_type': competition.user_type,
            'time_created': competition.time_created,
        })


class CompetitionStageList(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, competition, offset=0, limit=10):
        """获取竞赛的阶段列表
        :param offset: 偏移量
        :param limit: 数量上限

        :return:
            count: 阶段总数
            list: 阶段列表
                id: 阶段ID
                stage: 阶段名称:0:前期宣传, 1:报名, 2:预赛, 3:周赛, 4:月赛, 5:中间赛, 6:结束
                time_started: 开始时间
                time_ended: 结束时间
                time_created: 创建时间
        """

        c = competition.stages.count()
        qs = competition.stages.all().order_by("status")[offset: offset + limit]
        l = [{'id': p.id,
              'status': p.status,
              'time_started': p.time_started,
              'time_ended': p.time_ended,
              'time_created': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})


class CompetitionAwardList(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, competition, offset=0, limit=10):
        """获取竞赛的评比列表
        :param offset: 偏移量
        :param limit: 数量上限

        :return:
            count: 评比总数
            list: 评比列表
                id: 评比ID
                team_id: 团队ID
                team_name: 团队名称
                icon: 团队头像
                award: 获奖情况
                time_created: 创建时间
        """

        c = competition.awards.count()
        qs = competition.awards.all()[offset: offset + limit]
        l = [{'id': p.id,
              'team_id': p.team.id,
              'team_name': p.team.name,
              'icon': p.team.icon,
              'award': p.award,
              'time_created': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})


class CompetitionNotification(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, competition, offset=0, limit=10):
        """获取竞赛通知列表
        :param offset: 偏移量
        :param limit: 数量上限

        :return:
            count: 通知总数
            list: 通知列表
                id: 阶段ID
                stage: 阶段名称:0:前期宣传, 1:报名, 2:预赛, 3:周赛, 4:月赛, 5:中间赛, 6:结束
                notification: 通知内容
                time_created: 创建时间
        """

        c = competition.notifications.count()
        qs = competition.notifications.all().order_by(
            "-time_created")[offset: offset + limit]
        l = [{'id': p.id,
              'status': p.status,
              'notification': p.notification,
              'time_created': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})
    

class CompetitionFileList(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, competition, offset=0, limit=10):
        if not hasattr(request.user, 'rated_team_participators'):
            abort(403)
            return
        teams = request.user.rated_team_participators.values_list('team_id', flat=True)
        c = File.objects.filter(competition=competition, status=competition.status, team_id__in=teams).count()
        qs = File.objects.filter(competition=competition, status=competition.status, team_id__in=teams).order_by(
            "-time_created")[offset: offset + limit]
        l = [{'id': p.id,
              'team': p.team.name,
              'file': p.file,
              'type': p.type,
              'time_created': p.time_created,
              'score': p.score} for p in qs]
        return JsonResponse({'count': c, 'list': l})


class CompetitionFile(View):
    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取团队的上传文件信息
        :param offset: 偏移量
        :param limit: 数量上限

        :return:
            count: 参加的竞赛总数
            list: 竞赛的文件上传情况列表
                competition_id: 竞赛ID
                name: 竞赛名称
                status: 竞赛阶段0:前期宣传, 1:报名, 2:预赛, 3:周赛, 4:月赛, 5:中间赛, 6:结束
                time_id: 团队ID
                file: 上传的文件
        """

        c = team.competitions.count()
        rs = team.competitions.all()[offset: offset + limit]
        l = []
        for r in rs:
            t = dict()
            t['competition_id'] = r.competition.id
            t['name'] = r.competition.name
            t['team_id'] = team.id
            t['status'] = r.competition.status
            t['file'] = []
            try:
                files = r.competition.team_files.filter(
                    team=team, status=r.competition.status)
            except ObjectDoesNotExist:
                pass
            else:
                for f in files:
                    t['file'].append({
                        'file': f.file,
                        'file_id': f.id,
                        'score': f.score,
                        'comment': f.comment,
                        'type': f.type,
                    })
            l.append(t)
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    @validate_args({
        'type': forms.IntegerField(required=False),
    })
    def post(self, request, competition, team, **kwargs):
        """上传文件"""

        if request.user != team.owner:
            abort(404, '只有队长才可以上传文件')
        if team.competitions.filter(competition=competition).count() == 0:
            abort(404, '未参加该竞赛')

        file = request.FILES.get('file')
        if not file:
            abort(400, '文件上传失败')

        filename = save_uploaded_file(
            file, competition.id, competition.status, team.id)
        if filename:
            try:
                competition_file = competition.team_files.get(
                    status=competition.status, team=team, type=kwargs['type'])
                competition_file.file = filename
                competition_file.save()
            except ObjectDoesNotExist:
                competition.team_files.create(
                    file=filename,status=competition.status, team=team, type=kwargs['type'])
            abort(200)
        abort(400, '文件保存失败')


class CompetitionFileExpert(View):
    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    @validate_args({
        'expert_id': forms.IntegerField(),
    })
    def post(self, request, competition, team, expert_id):
        expert = User.objects.filter(pk=expert_id).get()
        CompetitionTeamParticipator.objects.filter(
            competition=competition,
            team=team,
        ).update(rater=expert)
        abort(200)


class CompetitionFileScore(View):
    @fetch_object(File.objects, 'file')
    @require_verification_token
    @validate_args({
        'score': forms.CharField(),
        'comment': forms.CharField(required=False),
    })
    def post(self, request, file, score='', comment=''):
        file.score=score
        file.comment=comment
        file.save()
        sum = 0
        for f in File.objects.filter(competition=file.competition, team=file.team, status=file.status):
            sum += int(f.score)
        CompetitionTeamParticipator.objects.filter(competition=file.competition, team=file.team).update(score=sum)
        abort(200)

class CompetitionTeamScore(View):
    @fetch_object(CompetitionTeamParticipator.objects, 'team_participator')
    @require_verification_token
    @validate_args({
        'score': forms.CharField(),
    })
    def post(self, request, team_participator, score=''):
        team_participator.score=score
        team_participator.save()
        abort(200)

class CompetitionExpertList(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_verification_token
    def get(self, request, competition):
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

class TeamParticipatorList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name', '-score')

    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'final': forms.BooleanField(required=False),
    })
    def get(self, request, competition, offset=0, limit=10, order=1, final=True):
        """获取报名团队列表"""

        k = self.ORDERS[order]
        c = competition.team_participators.filter(final=final).count()
        qs = competition.team_participators.filter(final=final).all().order_by(
            k)[offset: offset + limit]
        l = [{'id': p.team.id,
              'name': p.team.name,
              'icon_url': p.team.icon,
              'final': p.final} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Competition.enabled, 'competition')
    @validate_args({'team_id': forms.IntegerField()})
    @require_verification_token
    def post(self, request, competition, team_id):
        """报名"""

        if competition.status != 1:
            abort(403, '非报名阶段')
        c = competition.team_participators.count()
        if competition.allow_team != 0 and c >= competition.allow_team:
            abort(403, '参赛者已满')

        try:
            team = Team.enabled.get(id=team_id)
        except Team.DoesNotExist:
            abort(400, '团队不存在')
        else:
            if competition.province and competition.province != team.province:
                abort(403, '团队所在地区不符')
            if competition.city and (competition.city != team.city and competition.city.replace('市', '') != team.city.replace('市', '')):
                abort(403, '团队所在地区不符')
            for m in team.members.all():
                if m.user.is_verified not in [2, 4]:
                    abort(403, '团队成员未实名认证')
                if competition.user_type != 0:
                    if competition.user_type == 1 and m.user.role != "学生":
                        abort(403, '团队成员角色不符')
                    elif competition.user_type == 2 and m.user.role != "教师":
                        abort(403, '团队成员角色不符')
                    elif competition.user_type == 3 and \
                                    m.user.role != "在职":
                        abort(403, '团队成员角色不符')
                if competition.unit and competition.unit != m.user.unit1:
                    abort(403, '团队成员学校不符')
            if not competition.team_participators.filter(team=team).exists():
                competition.team_participators.create(team=team)
            abort(200)


class Search(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, order=1, **kwargs):
        """
        搜索竞赛

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 活动名包含字段

        :return:
            count: 竞赛总数
            list: 竞赛列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
                status:
                province:
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        qs = Competition.enabled.filter(name__icontains=kwargs['name'])
        c = qs.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created,
              'status': a.status,
              'province': a.province} for a in qs.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})


class Screen(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(required=False, max_length=20),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'allow_team': forms.IntegerField(required=False, min_value=0),
        'unit1': forms.CharField(required=False, max_length=20),
        'user_type': forms.IntegerField(
            required=False, min_value=0, max_value=3),
        'time_started': forms.DateField(required=False),
        'time_ended': forms.DateField(required=False),
    })
    def get(self, request, offset=0, limit=10, order=1, **kwargs):
        """
        筛选竞赛

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 竞赛名包含字段
            status: 竞赛阶段0:前期宣传, 1:报名, 2:预赛, 3:周赛, 4:月赛, 5:中间赛, 6:结束
            province: 省
            city: 市
            allow_team: 竞赛允许人数上限,0:不限人数
            unit1: 机构
            user_type: 允许人员身份,0:不限, 1:学生, 2:教师, 3:在职
            time_started: 开始时间下限
            time_ended: 结束时间上限

        :return:
            count: 竞赛总数
            list: 竞赛列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
                province:
                status:
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        qs = Competition.enabled
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称段检索
            qs = qs.filter(name__icontains=name)
        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            qs = qs.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            qs = qs.filter(city=city)
        unit1 = kwargs.pop('unit1', '')
        if unit1:
            # 按机构筛选
            qs = qs.filter(unit1=unit1)
        user_type = kwargs.pop('user_type', None)
        if user_type is not None:
            # 按参与者身份筛选
            qs = qs.filter(user_type=user_type)
        status = kwargs.pop('status', None)
        if status is not None:
            # 按活动阶段筛选
            qs = qs.filter(status=status)
        allow_team = kwargs.pop('allow_team', '')
        if allow_team:
            # 按人数上限筛选
            qs = qs.filter(allow_team__lte=allow_team)
        time_started = kwargs.pop('time_started', '')
        if time_started:
            # 按开始时间下限筛选
            qs = qs.filter(time_started__gte=time_started)
        time_ended = kwargs.pop('time_ended', '')
        if time_ended:
            # 按结束时间上限筛选
            qs = qs.filter(time_ended__lte=time_ended)

        qs = qs.all()
        c = qs.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created,
              'province': a.province,
              'status': a.status} for a in qs.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})
