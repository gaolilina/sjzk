from django import forms
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from ..models import UserVote, UserVoteOption, UserVoteOptionAdvocator, LabVote, LabVoteOption, LabVoteOptionAdvocator, User, Lab
from ..utils import abort
from ..utils.decorators import *


__all__ = ['UserList', 'UserDetail', 'UserOption',
           'LabList', 'LabDetail', 'LabOption']


class UserList(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(User.enabled, 'user')
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        k = self.ORDERS[order]
        c = user.votes.count()
        qs = user.votes.order_by(k)[offset: offset + limit]
        l = [{'id': a.id,
              'content': a.content,
              'owner': a.owner.id,
              'time_created': a.time_created,
              'deadline': a.deadline,
              'is_closed': a.is_closed} for a in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(User.enabled, 'user')
    @require_token
    @validate_args({
        'content': forms.CharField(required=False),
        'deadline': forms.DateTimeField(required=False),
        'is_closed': forms.IntegerField(required=False),
    })
    def post(self, request, user, content='', deadline=None, is_closed=None):
        if request.user == user:
            v = UserVote.objects.create(
                content=content,
                deadline=deadline,
                is_closed=(True if is_closed == 1 else False),
                owner=user
            )
            return JsonResponse({'id': v.id})
        abort(200)

class UserDetail(View):
    @fetch_object(UserVote.enabled, 'vote')
    @require_token
    def get(self, request, vote):
        c = vote.options.count()
        qs = vote.options.all()
        l = [{'id': p.id,
              'content': p.content,
              'chooser': p.advocators.count()} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(UserVote.enabled, 'vote')
    @require_token
    @validate_args({
        'content': forms.CharField(required=False),
        'deadline': forms.DateTimeField(required=False),
        'is_closed': forms.IntegerField(required=False),
    })
    def post(self, request, vote, content='', deadline=None, is_closed=None):
        if request.user == vote.owner:
            if content != '':
                UserVoteOption.objects.create(
                    entity=vote,
                    content=content
                )
            if deadline is not None:
                vote.deadline = deadline
            if is_closed is not None:
                vote.is_closed = True if is_closed == 1 else False
            vote.save()
        abort(200)


class UserOption(View):
    @fetch_object(UserVoteOption.enabled, 'option')
    @require_token
    def get(self, request, option):
        c = option.advocators.count()
        qs = option.advocators.all()
        l = [{'id': p.id,
              'user': p.user.id,
              'user_name': p.user.name,
              'time_created': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})
    
    @fetch_object(UserVoteOption.enabled, 'option')
    @require_token
    @validate_args({
        'content': forms.CharField(required=False),
    })
    def post(self, request, option, content=''):
        if request.user == option.entity.owner:
            if content != '':
                option.content = content
                option.save()
        else:
            UserVoteOptionAdvocator.objects.create(
                entity=option,
                user=request.user
            )
        abort(200)



class LabList(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Lab.enabled, 'lab')
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        k = self.ORDERS[order]
        c = lab.votes.count()
        qs = lab.votes.order_by(k)[offset: offset + limit]
        l = [{'id': a.id,
              'content': a.content,
              'owner': a.owner.id,
              'time_created': a.time_created,
              'deadline': a.deadline,
              'is_closed': a.is_closed} for a in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Lab.enabled, 'lab')
    @require_token
    @validate_args({
        'content': forms.CharField(required=False),
        'deadline': forms.DateTimeField(required=False),
        'is_closed': forms.IntegerField(required=False),
    })
    def post(self, request, lab, content='', deadline=None, is_closed=None):
        if request.user == lab.owner:
            v = LabVote.objects.create(
                content=content,
                deadline=deadline,
                is_closed=(True if is_closed == 1 else False),
                owner=lab
            )
            return JsonResponse({'id': v.id})
        abort(200)

class LabDetail(View):
    @fetch_object(LabVote.enabled, 'vote')
    @require_token
    def get(self, request, vote):
        c = vote.options.count()
        qs = vote.options.all()
        l = [{'id': p.id,
              'content': p.content,
              'chooser': p.advocators.count()} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(LabVote.enabled, 'vote')
    @require_token
    @validate_args({
        'content': forms.CharField(required=False),
        'deadline': forms.DateTimeField(required=False),
        'is_closed': forms.IntegerField(required=False),
    })
    def post(self, request, vote, content='', deadline=None, is_closed=None):
        if request.user == vote.owner.owner:
            if content != '':
                LabVoteOption.objects.create(
                    entity=vote,
                    content=content
                )
            if deadline is not None:
                vote.deadline = deadline
            if is_closed is not None:
                vote.is_closed = True if is_closed == 1 else False
            vote.save()
        abort(200)


class LabOption(View):
    @fetch_object(LabVoteOption.enabled, 'option')
    @require_token
    def get(self, request, option):
        c = option.advocators.count()
        qs = option.advocators.all()
        l = [{'id': p.id,
              'user': p.user.id,
              'user_name': p.user.name,
              'time_created': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})
    
    @fetch_object(LabVoteOption.enabled, 'option')
    @require_token
    @validate_args({
        'content': forms.CharField(required=False),
    })
    def post(self, request, option, content=''):
        if request.user == option.entity.owner.owner:
            if content != '':
                option.content = content
                option.save()
        else:
            LabVoteOptionAdvocator.objects.create(
                entity=option,
                user=request.user
            )
        abort(200)