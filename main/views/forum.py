from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from ..models import ForumBoard, ForumPost
from ..utils import abort
from ..utils.decorators import *


__all__ = ['BoardList', 'Board', 'PostList', 'Post']


class BoardList(View):
    available_orders = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1, owned_only=False):
        """获取板块列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 创建时间升序
            1: 创建时间降序（默认值）
            2: 版名升序
            3: 版名降序
        :param owned_only: 是否只显示自己创建的版块列表
        :return:
            count: 板块总数
            list: 板块列表
                id: 板块ID
                name: 板块名
                description: 版块描述
                owner_id: 版主
                owner_name: 版主昵称
                is_system_board；是否是系统板块
                time_created: 创建时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        qs = request.user.forum_boards.filter(enabled=True) if owned_only \
            else ForumBoard.enabled
        c = qs.count()
        boards = qs.order_by(k)[i:j]
        l = [{'id': b.id,
              'name': b.name,
              'description': b.description,
              'owner_id': b.owner.id,
              'owner_name': b.owner.name,
              'is_system_board': b.is_system_board,
              'time_created': b.time_created} for b in boards]
        return JsonResponse({'count': c, 'list': l})

    @require_token
    @validate_args({
        'name': forms.CharField(min_length=1, max_length=20),
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, **kwargs):
        """新建板块

        :param kwargs:
            name: 板块名称
            description: 板块描述
        :return: board_id: 板块id
        """
        name = kwargs['name']
        description = kwargs['description']

        if ForumBoard.enabled.filter(name=name).exists():
            abort(403)

        b = request.user.forum_boards.create(name=name, description=description)
        return JsonResponse({'board_id': b.id})


class Board(View):
    @require_token
    @fetch_object(ForumBoard, 'board')
    def delete(self, request, board):
        """删除版块，只是改变is_enabled字段为False，数据库中并不删除"""

        if request.user != board.owner:
            abort(403)
        board.is_enable = False
        board.save()
        abort(200)


class PostList(View):
    @require_token
    @validate_args({'offset': forms.IntegerField(required=False, min_value=0)})
    @fetch_object(ForumBoard, 'board')
    def get(self, request, board, offset=0, limit=10):
        """获取主题帖列表

        :param offset: 偏移量
        :return:
            count: 帖子总数
            list: 帖子列表
                id: 帖子ID
                title: 标题
                content: 内容
                author_id: 作者ID
                author_name: 作者昵称
                time_created: 创建时间
        """
        i, j = offset, offset + limit
        qs = board.posts.filter(~Q(main_post=None))
        c = qs.count()
        posts = qs[i:j]
        l = [{'id': p.id,
              'title': p.title,
              'content': p.content,
              'author_id': p.author.id,
              'author_name': p.author.name,
              'time_created': p.time_created} for p in posts]
        return JsonResponse({'count': c, 'list': l})

    @require_token
    @fetch_object(ForumPost, 'board')
    def post(self, request, board, title, content):
        """发主题帖"""

        p = board.posts.create(author=request.user, title=title, content=content)
        return JsonResponse({'post_id': p.id})


class Post(View):
    @require_token
    @validate_args({'offset': forms.IntegerField(required=False, min_value=0)})
    @fetch_object(ForumPost, 'post')
    def get(self, request, post, offset=0, limit=10):
        """获取主题帖的回帖列表

        :param offset: 偏移量
        :return:
            count: 帖子总数
            list: 帖子列表
                id: 帖子ID
                title: 标题
                content: 内容
                author_id: 作者ID
                author_name: 作者昵称
                time_created: 创建时间
        """
        if post.main_post is not None:
            abort(400)

        i, j = offset, offset + limit
        qs = post.posts
        c = qs.count()
        posts = qs[i:j]
        l = [{'id': p.id,
              'title': p.title,
              'content': p.content,
              'author_id': p.author.id,
              'author_name': p.author.name,
              'time_created': p.time_created} for p in posts]
        return JsonResponse({'count': c, 'list': l})

    @require_token
    @fetch_object(ForumPost, 'post')
    def post(self, request, post, title, content):
        """回主题帖"""

        p = post.posts.create(board=post.board, author=request.user,
                              title=title, content=content)
        return JsonResponse({'post_id': p.id})

    @require_token
    @fetch_object(ForumPost, 'post')
    def delete(self, request, post):
        """删除帖子"""

        if request.user != post.author or request.user != post.board.owner:
            abort(403)
        post.delete()
        abort(200)