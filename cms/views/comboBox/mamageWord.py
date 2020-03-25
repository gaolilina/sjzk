from django import forms

from cms.util.getWord import getDetail

from modellib.models.comboBox import ComboBox
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
#from util.decorator.permission import cms_permission

class mamageComboBox(BaseView):
    '''管理端根据id获取选项，提交新的选项,根据id删除选项数据'''
    @cms_auth
    @validate_args({
        'word_id': forms.IntegerField(),
    })
    def get(self, request, word_id, **kwargs):                #根据id查询选项详细信息
        dict = getDetail(word_id, True)
        return self.success({
            'result': dict
        })

    @cms_auth
    @validate_args({
        'value': forms.CharField(max_length=254),
        'word_id': forms.IntegerField(),
    })
    @fetch_object(ComboBox.objects, 'parent', 'word_id')

    def post(self, request, value, parent, **kwargs):       #创建一级以下的选项

        ComboBox.objects.create(value=value, parent=parent)
        return self.success()

    @cms_auth
    @validate_args({
        'word_id': forms.IntegerField(),
    })
    def delete(self, request, word_id):                             #删除指定id的选项
        combo = ComboBox.objects.filter(id=word_id)
        if not combo:
            return self.fail(code=3, msg='该选项不存在')
        combo.delete()
        return self.success()


class getComboBox(BaseView):
    '''管理端根据value查询选项，只能查找第一级，不向下查找'''
    @cms_auth
    @validate_args({
        'value': forms.CharField(required=False, max_length=254),
    })
    def get(self, request, value=""):                            #管理端根据value模糊查询选项
        res = ComboBox.objects.filter(value__contains=value, parent=None)
        dict = []
        for comb in res:
            dict.append({
                'value' : comb.value,
                'id' : comb.id,
            })
        return self.success({
            'result': dict
        })

    @cms_auth
    @validate_args({
        'key': forms.CharField(max_length=254),
        'value': forms.CharField(max_length=254),
    })
    def post(self, request, key, value, **kwargs):                #创建一级选项

        if ComboBox.objects.filter(key=key):
            return self.fail(code=2,msg='key值不能重复')

        ComboBox.objects.create(key=key, value=value)
        return self.success()
