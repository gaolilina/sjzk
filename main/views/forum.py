from django import forms
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, check_object_id, \
    validate_input, validate_json_input, process_uploaded_image
from main.models.forum import Board, Post
from main.responses import *


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
    @validate_input(get_dict)
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
                owners: 版主,格式:{'id': 1, 'name': zq, 'icon_url': *}
                is_system_board；是否是系统板块
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]

        c = Board.enabled.count()
        boards = Board.enabled.order_by(k)[i:j]
        l = [{'id': b.id,
              'name': b.name,
              'owner': {'id': b.owner.id,
                        'name': b.owner.name,
                        'icon_url': b.owner.icon_url},
              'is_system_board': b.is_system_board,
              'create_time': b.create_time} for b in boards]
        return JsonResponse({'count': c, 'list': l})


class BoardSelf(View):
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

        try:
            with transaction.atomic():
                try:
                    board = Board(name, description, request.user)
                    board.save()
                except IntegrityError:
                    return Http400('board name already exists')
                if 'is_system_board' in data:
                    board.is_system_board = data['is_system_board']
                    board.save()
                return JsonResponse({'board_id': board.id})
        except IntegrityError:
            return Http400()

    @require_token
    @check_object_id(Board.enabled, 'board')
    def delete(self, request, board):
        if request.user != board.owner:
            return Http403('recent user has no authority')
        board.is_enabled = False
        return Http200()


class Posts(View):
    pass


class PostSelf(View):
    pass