from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from util.decorator.param import validate_args, fetch_object
from ..models import ForumBoard, ForumPost
from ..utils import abort, action
from ..utils.dfa import check_bad_words
from ..utils.decorators import *


__all__ = [
    'BoardList', 'Board', 'PostList', 'Post', 'SearchBoard', 'SearchPost']


class BoardList(View):
    available_orders = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
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
                icon_url: 版主头像
                is_system_board；是否是系统板块
                time_created: 创建时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        if owned_only:
            fetch_user_by_token(request, True)

        qs = request.user.forum_boards.filter(enabled=True) if owned_only \
            else ForumBoard.enabled
        c = qs.count()
        boards = qs.order_by(k)[i:j]
        l = [{'id': b.id,
              'name': b.name,
              'description': b.description,
              'owner_id': b.owner.id,
              'owner_name': b.owner.name,
              'icon_url': b.owner.icon,
              'is_system_board': b.is_system_board,
              'time_created': b.time_created} for b in boards]
        return JsonResponse({'count': c, 'list': l, 'code': 0})

    @require_verification_token
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
            abort(403, '板块已存在')
        
        if check_bad_words(name) or check_bad_words(description):
            abort(400, '含有非法词汇')

        b = request.user.forum_boards.create(name=name, description=description)
        # 发动态
        action.send_forum(request.user, b)
        return JsonResponse({'board_id': b.id, 'code': 0})


class Board(View):
    @require_verification_token
    @fetch_object(ForumBoard.enabled, 'board')
    def delete(self, request, board):
        """删除版块，只是改变is_enabled字段为False，数据库中并不删除"""

        if request.user != board.owner:
            abort(403, '非法操作')
        board.is_enable = False
        board.save()
        abort(200)


class PostList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    @fetch_object(ForumBoard.enabled, 'board')
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
                icon_url: 作者头像
                time_created: 创建时间
        """
        i, j = offset, offset + limit
        qs = board.posts.filter(Q(main_post=None))
        c = qs.count()
        posts = qs[i:j]
        l = [{'id': p.id,
              'title': p.title,
              'content': p.content,
              'author_id': p.author.id,
              'author_name': p.author.name,
              'icon_url': p.author.icon,
              'time_created': p.time_created} for p in posts]
        return JsonResponse({'count': c, 'list': l, 'code': 0})

    @require_verification_token
    @fetch_object(ForumBoard.enabled, 'board')
    @validate_args({
        'title': forms.CharField(max_length=20),
        'content': forms.CharField(max_length=300),
    })
    def post(self, request, board, title, content):
        """发主题帖"""
        
        if check_bad_words(title) or check_bad_words(content):
            abort(400, '含有非法词汇')

        p = board.posts.create(author=request.user, title=title, content=content)
        return JsonResponse({'post_id': p.id, 'code': 0})


class Post(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    @fetch_object(ForumPost.objects, 'post')
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
                icon_url: 作者头像
                time_created: 创建时间
        """
        if post.main_post is not None:
            abort(400, '无主题帖')

        i, j = offset, offset + limit
        qs = post.posts.all()
        c = qs.count()
        posts = qs[i:j]
        l = [{'id': p.id,
              'title': p.title,
              'content': p.content,
              'author_id': p.author.id,
              'author_name': p.author.name,
              'icon_url': p.author.icon,
              'time_created': p.time_created} for p in posts]
        return JsonResponse({'count': c, 'list': l, 'code': 0})

    @require_verification_token
    @fetch_object(ForumPost.objects, 'post')
    @validate_args({
        'title': forms.CharField(max_length=20),
        'content': forms.CharField(max_length=300),
    })
    def post(self, request, post, title, content):
        """回主题帖"""

        if check_bad_words(title) or check_bad_words(content):
            abort(400, '含有非法词汇')

        p = post.posts.create(main_post=post, board=post.board,
                              author=request.user, title=title, content=content)
        return JsonResponse({'post_id': p.id, 'code': 0})

    @require_verification_token
    @fetch_object(ForumPost.objects, 'post')
    def delete(self, request, post):
        """删除帖子"""

        if request.user != post.author or request.user != post.board.owner:
            abort(403, '操作非法')
        post.delete()
        abort(200)


class SearchBoard(View):
    available_orders = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, board, offset=0, limit=10, order=1, **kwargs):
        """根据名称搜索板块

        :param offset: 偏移量
        :return:
            count: 帖子总数
            list: 帖子列表
                id: 帖子ID
                title: 标题
                content: 内容
                author_id: 作者ID
                author_name: 作者昵称
                icon_url: 作者头像
                time_created: 创建时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        qs = request.user.forum_boards.filter(
            Q(enabled=True) & Q(name__icontains=kwargs['name']))
        c = qs.count()
        boards = qs.order_by(k)[i:j]
        l = [{'id': b.id,
              'name': b.name,
              'description': b.description,
              'owner_id': b.owner.id,
              'owner_name': b.owner.name,
              'icon_url': b.owner.icon,
              'is_system_board': b.is_system_board,
              'time_created': b.time_created} for b in boards]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class SearchPost(View):
    available_orders = ('time_created', '-time_created', 'title', '-title')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'title': forms.CharField(max_length=20),

    })
    @fetch_object(ForumBoard.enabled, 'board')
    def get(self, request, board, offset=0, limit=10, order=1, **kwargs):
        """根据标题搜索主题帖

        :param offset: 偏移量
        :return:
            count: 帖子总数
            list: 帖子列表
                id: 帖子ID
                title: 标题
                content: 内容
                author_id: 作者ID
                author_name: 作者昵称
                icon_url: 作者头像
                time_created: 创建时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        qs = board.posts.filter(Q(main_post=None) &
                                Q(title__icontains=kwargs['title']))
        c = qs.count()
        posts = qs.order_by(k)[i:j]
        l = [{'id': p.id,
              'title': p.title,
              'content': p.content,
              'author_id': p.author.id,
              'author_name': p.author.name,
              'icon_url': p.author.icon,
              'time_created': p.time_created} for p in posts]
        return JsonResponse({'count': c, 'list': l, 'code': 0})
