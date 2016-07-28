from django import forms
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.generic import View
from main.responses import *

from main.models.forum import Board, Post
from main.utils.decorators import require_token, fetch_object, \
    validate_args, validate_json_input


class Boards(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'name', '-name',
    ]

    @require_token
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取板块列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 板块总数
            list: 板块列表
                id: 板块ID
                name: 板块名
                owner_id: 版主
                owner_name: 版主昵称
                owner_icon_url: 版主头像URL
                is_system_board；是否是系统板块
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        c = Board.enabled.count()
        boards = Board.enabled.order_by(k)[i:j]
        l = [{'id': b.id,
              'name': b.name,
              'owner_id': b.owner.id,
              'owner_name': b.owner.name,
              'owner_icon_url': b.owner.icon_url,
              'is_system_board': b.is_system_board,
              'create_time': b.create_time} for b in boards]
        return JsonResponse({'count': c, 'list': l})


class BoardSelf(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'name', '-name',
    ]

    @require_token
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取自己创建的板块列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 板块总数
            list: 板块列表
                id: 板块ID
                name: 板块名
                owner_id: 版主
                owner_name: 版主昵称
                owner_icon_url: 版主头像URL
                is_system_board；是否是系统板块
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        c = Board.enabled.filter(owner=request.user).count()
        boards = Board.enabled.filter(owner=request.user).order_by(k)[i:j]
        l = [{'id': b.id,
              'name': b.name,
              'owner_id': b.owner.id,
              'owner_name': b.owner.name,
              'owner_icon_url': b.owner.icon_url,
              'is_system_board': b.is_system_board,
              'create_time': b.create_time} for b in boards]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'name': forms.CharField(min_length=1, max_length=20),
        'description': forms.CharField(min_length=1, max_length=100),
        'is_system_board': forms.BooleanField(required=False),
    }

    @require_token
    @validate_json_input(post_dict)
    def post(self, request, data):
        """
        新建板块

        :param data:
            name: 板块名称
            description: 板块描述
            is_system_board: 是否为系统板块（默认为否）
        :return: board_id: 板块id
        """
        name = data['name']
        description = data['description']

        num = Board.enabled.filter(name=name).count()
        if num > 0:
            return Http400('board name already exists')
        try:
            with transaction.atomic():
                board = Board(name, description, request.user)
                board.save()

                if 'is_system_board' in data:
                    board.is_system_board = data['is_system_board']
                    board.save()
                return JsonResponse({'board_id': board.id})
        except IntegrityError:
            return Http400()

    @require_token
    @fetch_object(Board.enabled, 'board')
    def delete(self, request, board):
        """
        删除版块，只是改变is_enabled字段为False，数据库中并不删除

        :param board_id: 版块ID
        """
        if request.user != board.owner:
            return Http403('recent user has no authority')
        posts = Post.enabled.filter(board=board)
        with transaction.atomic():
            board.is_enabled = False
            # 删除版块中所有的帖子
            if posts:
                for p in posts:
                    p.is_enabled = False
                    p.save()
            board.save()
            return Http200()


class Posts(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
    ]

    @require_token
    @validate_args(get_dict)
    @fetch_object(Board.enabled, 'board')
    def get(self, request, board, offset=0, limit=10, order=1):
        """
        获取帖子列表

        :param board_id: 版块ID
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
        :return:
            count: 帖子总数
            list: 帖子列表
                id: 帖子ID
                content: 内容
                board_id: 帖子所属版块ID
                author_id: 作者ID
                author_name: 作者昵称
                author_icon_url: 作者头像URL
                is_main_post: 是否是主题帖
                is_fixed: 是否置顶帖
                create_time: 创建时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        c = Post.enabled.filter(board=board).count()
        posts = Post.enabled.filter(board=board).order_by(k)[i:j]
        l = [{'id': p.id,
              'content': p.content,
              'board_id': p.board.id,
              'author_id': p.author.id,
              'author_name': p.author.name,
              'author_icon_url': p.author.icon_url,
              'is_main_post': p.is_main_post,
              'is_fixed': p.is_fixed,
              'create_time': p.create_time} for p in posts]
        return JsonResponse({'count': c, 'list': l})


class PostSelf(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
    ]

    @require_token
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取自己发表的帖子列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
        :return:
            count: 帖子总数
            list: 帖子列表
                id: 帖子ID
                content: 内容
                board_id: 所属版块ID
                board_name: 版块名称
                author_id: 作者ID
                author_name: 作者昵称
                author_icon_url: 作者头像URL
                is_main_post: 是否是主题帖
                is_fixed: 是否置顶帖
                create_time: 创建时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        c = Post.enabled.filter(author=request.user).count()
        posts = Post.enabled.filter(author=request.user).order_by(k)[i:j]
        l = [{'id': p.id,
              'content': p.content,
              'board_id': p.board.id,
              'board_name': p.board.name,
              'author_id': p.author.id,
              'author_name': p.author.name,
              'author_icon_url': p.author.icon_url,
              'is_main_post': p.is_main_post,
              'is_fixed': p.is_fixed,
              'create_time': p.create_time} for p in posts]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'content': forms.CharField(min_length=1, max_length=250),
        'is_main_post': forms.BooleanField(required=False),
        'is_fixed': forms.BooleanField(required=False),
    }

    @fetch_object(Board.enabled, 'board')
    @require_token
    @validate_json_input(post_dict)
    def post(self, request, board, data):
        """
        新建帖子

        :param board_id: 所属版块ID
        :param data:
            content: 帖子内容
            is_main_post: 是否为主题帖（默认为否）
            is_fixed: 是否为置顶帖（默认为否）
        :return: post_id: 帖子id
        """
        content = data['content']

        try:
            with transaction.atomic():
                post = Post(request.user, board, content)
                post.save()

                if 'is_main_post' in data:
                    post.is_main_post = data['is_main_post']
                    post.save()
                if 'is_fixed' in data:
                    post.is_fixed = data['is_fixed']
                    post.save()
                return JsonResponse({'post_id': post.id})
        except IntegrityError:
            return Http400()

    @require_token
    @fetch_object(Board.enabled, 'board')
    @fetch_object(Post.enabled, 'post')
    def delete(self, request, board, post):
        """
        删除帖子(版主或发布者有权利)，只是改变is_enabled字段为False，数据库中并不删除

        :param board_id: 帖子所属版块ID
        :param post_id: 帖子ID
        """
        if post.board != board:
            return Http400('related post does not exist')
        if (request.user != post.owner) & (request.user != board.owner):
            return Http403('recent user has no authority')
        post.is_enabled = False
        post.save()
        return Http200()
