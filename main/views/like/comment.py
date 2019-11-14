#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from main.models import UserComment, TeamComment, ActivityComment, CompetitionComment, UserActionComment, \
    TeamActionComment
from main.views.like import ILikeSomethingSimple as ILikeSomething
from util.decorator.param import fetch_object


class ILikeUserComment(ILikeSomething):
    @fetch_object(UserComment.objects, 'comment')
    def get(self, request, comment):
        return super().get(request, comment)

    @fetch_object(UserComment.objects, 'comment')
    def post(self, request, comment):
        return super().post(request, comment)

    @fetch_object(UserComment.objects, 'comment')
    def delete(self, request, comment):
        return super().delete(request, comment)


class ILikeTeamComment(ILikeSomething):
    @fetch_object(TeamComment.objects, 'comment')
    def get(self, request, comment):
        return super().get(request, comment)

    @fetch_object(TeamComment.objects, 'comment')
    def post(self, request, comment):
        return super().post(request, comment)

    @fetch_object(TeamComment.objects, 'comment')
    def delete(self, request, comment):
        return super().delete(request, comment)


class ILikeActivityComment(ILikeSomething):
    @fetch_object(ActivityComment.objects, 'comment')
    def get(self, request, comment):
        return super().get(request, comment)

    @fetch_object(ActivityComment.objects, 'comment')
    def post(self, request, comment):
        return super().post(request, comment)

    @fetch_object(ActivityComment.objects, 'comment')
    def delete(self, request, comment):
        return super().delete(request, comment)


class ILikeCompetitionComment(ILikeSomething):
    @fetch_object(CompetitionComment.objects, 'comment')
    def get(self, request, comment):
        return super().get(request, comment)

    @fetch_object(CompetitionComment.objects, 'comment')
    def post(self, request, comment):
        return super().post(request, comment)

    @fetch_object(CompetitionComment.objects, 'comment')
    def delete(self, request, comment):
        return super().delete(request, comment)


class ILikeUserActionComment(ILikeSomething):
    @fetch_object(UserActionComment.objects, 'comment')
    def get(self, request, comment):
        return super().get(request, comment)

    @fetch_object(UserActionComment.objects, 'comment')
    def post(self, request, comment):
        return super().post(request, comment)

    @fetch_object(UserActionComment.objects, 'comment')
    def delete(self, request, comment):
        return super().delete(request, comment)


class ILikeTeamActionComment(ILikeSomething):
    @fetch_object(TeamActionComment.objects, 'comment')
    def get(self, request, comment):
        return super().get(request, comment)

    @fetch_object(TeamActionComment.objects, 'comment')
    def post(self, request, comment):
        return super().post(request, comment)

    @fetch_object(TeamActionComment.objects, 'comment')
    def delete(self, request, comment):
        return super().delete(request, comment)
