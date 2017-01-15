import json
from datetime import datetime, timedelta

from django.core.management import BaseCommand

from ...models import User, Team, UserFeature, TeamFeature
from ChuangYi import settings


class Command(BaseCommand):
    """构建用户、团队等实体的特征模型"""

    def handle(self, *args, **kwargs):
        self.time_started = datetime.now()
        self.build_user_models()
        self.stdout.write("%s: user models updated" % datetime.now())
        self.build_team_models()
        self.stdout.write("%s: team models updated" % datetime.now())

    def build_user_models(self):
        users = User.enabled.all()
        for u in users:
            model = dict()

            # 固定部分
            for i in u.tags.all():
                model[i.name] = settings.USER_TAG_SCORE

            for i in u.teams.all():
                for j in i.team.tags.all():
                    if j.name in model:
                        model[j.name] += settings.USER_TEAM_TAG_SCORE
                    else:
                        model[j.name] = settings.USER_TEAM_TAG_SCORE

            for i in u.followed_users.all():
                for j in i.followed.tags.all():
                    if j.name in model:
                        model[j.name] += settings.USER_FOLLOWED_TAG_SCORE
                    else:
                        model[j.name] = settings.USER_FOLLOWED_TAG_SCORE

            for i in u.followed_teams.all():
                for j in i.followed.tags.all():
                    if j.name in model:
                        model[j.name] += settings.USER_FOLLOWED_TAG_SCORE
                    else:
                        model[j.name] = settings.USER_FOLLOWED_TAG_SCORE

            # 可变部分
            t = self.time_started - \
                timedelta(days=settings.USER_BEHAVIOR_ANALYSIS_CIRCLE)
            behaviors = u.behaviors.filter(time_created__gte=t)
            for b in behaviors:
                # 行为类型判断
                if b.behavior == 'like':
                    score = settings.USER_LIKE_SCORE
                elif b.behavior == 'view':
                    score = settings.USER_VIEW_SCORE
                else:
                    raise Exception

                # 交互对象类型判断
                if b.object_type == 'user':
                    try:
                        obj = User.enabled.get(id=b.object_id)
                    except User.DoesNotExist:
                        continue
                elif b.object_type == 'team':
                    try:
                        obj = User.enabled.get(id=b.object_id)
                    except User.DoesNotExist:
                        continue
                else:
                    raise Exception

                # 记录标签分数
                for i in obj.tags.all():
                    if i.name in model:
                        model[i.name] += score
                    else:
                        model[i.name] = score
            # 保存
            user_model, created = UserFeature.objects.get_or_create(user=u)
            user_model.data = json.dumps(model)
            user_model.save()

    def build_team_models(self):
        teams = Team.enabled.all()
        for t in teams:
            model = dict()
            for i in t.tags.all():
                model[i.name] = settings.TEAM_TAG_SCORE

            for i in t.members.all():
                for j in i.user.tags.all():
                    if j.name in model:
                        model[j.name] += settings.TEAM_MEMBER_TAG_SCORE
                    else:
                        model[j.name] = settings.TEAM_MEMBER_TAG_SCORE

            team_model, created = TeamFeature.objects.get_or_create(team=t)
            team_model.data = json.dumps(model)
            team_model.save()
