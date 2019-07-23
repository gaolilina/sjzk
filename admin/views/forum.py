# Auto generated by forum.py
from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import *
from main.models.forum import *
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args


class ForumBoardView(View):
    @fetch_record(ForumBoard.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("forum/forum_board.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(ForumBoard.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'name': forms.CharField(max_length=20, ), 'description': forms.CharField(max_length=100, ),
        'time_created': forms.DateTimeField(required=False, ), 'is_system_board': forms.BooleanField(required=False),
        'is_enabled': forms.BooleanField(required=False),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("forum_board", mod.id, 1, request.user)

        template = loader.get_template("forum/forum_board.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class ForumBoardList(View):
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if request.GET.get("name") is not None:
            name = request.GET.get("name")
            template = loader.get_template("forum/forum_board_index.html")
            if ForumBoard == ForumPost:
                list = ForumPost.objects.filter(title__contains=name)
            else:
                list = ForumBoard.objects.filter(name__contains=name)
            context = Context({'name': name, 'list': list, 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("forum/forum_board_index.html")
            context = Context({'user': request.user})
            return HttpResponse(template.render(context))


class ForumPostView(View):
    @fetch_record(ForumPost.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("forum/forum_post.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(ForumPost.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'title': forms.CharField(max_length=20, ), 'content': forms.CharField(max_length=300, ),
        'time_created': forms.DateTimeField(required=False, ),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("forum_post", mod.id, 1, request.user)

        template = loader.get_template("forum/forum_post.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class ForumPostList(View):
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if request.GET.get("name") is not None:
            name = request.GET.get("name")
            template = loader.get_template("forum/forum_post_index.html")
            if ForumPost == ForumPost:
                list = ForumPost.objects.filter(title__contains=name)
            else:
                list = ForumPost.objects.filter(name__contains=name)
            context = Context({'name': name, 'list': list, 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("forum/forum_post_index.html")
            context = Context({'user': request.user})
            return HttpResponse(template.render(context))
