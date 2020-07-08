from django import forms
from django.http import JsonResponse

from main.utils import abort
from main.models import Activity
from main.models import Competition
from modellib.models.need import UserNeed
from util.base.view import BaseManyToManyView, BaseView
from util.decorator.auth import client_auth
from util.decorator.param import fetch_object, validate_args


class UserNeedList(BaseView):

    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField(required=False),
        'competition_id': forms.IntegerField(required=False),
    })
    @fetch_object(Activity.objects, 'activity', force=False)
    @fetch_object(Competition.objects, 'competition', force=False)
    def get(self, request, activity=None, competition=None, **kwargs):
        """获取用户当前发布需求"""
        qs = UserNeed.objects.filter(user=request.user, activity=activity, competition=competition)

        return self.success_list(request, qs, need_to_json)

    @client_auth
    @validate_args({
        'tags': forms.CharField(max_length=250),
        'desc': forms.CharField(max_length=250),
        'content': forms.CharField(max_length=250),
        'city': forms.CharField(max_length=20),
        'activity_id': forms.IntegerField(required=False),
        'competition_id': forms.IntegerField(required=False),
    })
    @fetch_object(Activity.objects, 'activity', force=False)
    @fetch_object(Competition.objects, 'competition', force=False)
    def post(self, request, tags, desc, content, city, activity=None, competition=None, **kwargs):
        """提交用户需求"""
        UserNeed.objects.create(field=tags, desc=desc, content=content, city=city, user=request.user, activity=activity, competition=competition)
        return self.success()


class DeleteMyUserNeed(BaseView):
    """删除需求"""
    @client_auth
    @fetch_object(UserNeed.objects, 'need')
    def delete(self, request, need):
        if need.user != request.user:
            return self.fail(1, '该需求不是您发布的，无权删除')
        UserNeed.objects.filter(id=need.id).delete()
        abort(200)


class IDoSomethingOnUserNeed(BaseManyToManyView):

    @fetch_object(UserNeed.objects, 'need')
    def post(self, request, need, field, **kwargs):
        return super().post(request, need, field)

    @fetch_object(UserNeed.objects, 'need')
    def delete(self, request, need, field, **kwargs):
        return super().delete(request, need, field)


class getUserNeedMatching(BaseView):
    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField(required=False),
        'competition_id': forms.IntegerField(required=False),
    })
    @fetch_object(Activity.objects, 'activity', force=False)
    @fetch_object(Competition.objects, 'competition', force=False)
    def get(self, request, activity=None, competition=None, **kwargs):
        """对竞赛，活动类需求进行匹配"""
        goodat = request.user.goodat
        if not goodat:
            abort(403, '无擅长标签')
        tags = [tag.split("-")[-1] for tag in goodat.split("；")]
        list = []

        qs = UserNeed.objects.filter(competition=competition, activity=activity)
        for need in qs:
            field = need.field.replace("；", ";", 10)
            fields = field.split(";")
            count = 0
            for field in fields:
                if field in tags:
                    count += 1

            if count != 0:
                list.append({"nums":count, "need":need_to_json(need)})

        return JsonResponse({'count': len(list), 'list': list})



class getUserNeedMatchingInFriend(BaseView):

    @client_auth
    def get(self, request, **kwargs):
        """对好友需求进行匹配"""
        goodat = request.user.goodat
        if not goodat:
            abort(403, '无擅长标签')

        tags = [tag.split("-")[-1] for tag in goodat.split("；")]

        needList = []
        for friend in request.user.friends.all():
            needList.append(friend.other_user.needs.all())

        list = []

        for item in needList:                  #一个好友发布的需求列表
            for need in item:                  #需求
                if need.competition != None or need.activity!=None:      #团队或活动需求跳过
                    continue
                field = need.field.replace("；", ";", 10)
                fields = field.split(";")
                count = 0
                for field in fields:
                    if field in tags:
                        count += 1

                if count != 0:
                    list.append({"nums": count, "need": need_to_json(need)})

        return JsonResponse({'count': len(list), 'list': list})



def need_to_json(need):
    return {
        'id': need.id,
        'user_id': need.user_id,
        'desc': need.desc,
        'content': need.content,
        'city': need.city,
        'count_likers': need.likers.all().count(),
        'tags': need.field,
    }
