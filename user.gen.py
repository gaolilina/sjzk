 # Auto generated by generate.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChuangYi.settings")
import django
from django.db import models
django.setup()

import inspect
import types
import codecs

import main.models.user as users

url_text = """# Auto generated by user.py
from django.conf.urls import url

from admin.views.user import *

urls = ["""

view_text = """# Auto generated by user.py
from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from main.models.user import *

from admin.utils.decorators import *
"""
view_class_text = """class {{cls_name}}View(View):
    @fetch_record({{cls_name}}.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("user/{{tbl_name}}.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record({{cls_name}}.objects, 'mod', 'id')
    @require_cookie
    @require_role('yz')
    @validate_args2({
        {{args}}
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("{{tbl_name}}", mod.id, 1, request.user)

        template = loader.get_template("user/{{tbl_name}}.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class {{cls_name}}List(View):
    @require_cookie
    @require_role('yz')
    @validate_args2({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = {{cls_name}}.objects.filter(user_id=kwargs["id"])
            template = loader.get_template("user/{{tbl_name}}_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:user:{{tbl_name}}', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            template = loader.get_template("user/index.html")
            if {{cls_name}} == User:
                redir = 'admin:user:user'
            else:
                redir = 'admin:user:{{tbl_name}}_list'
            context = Context({'name': name, 'list': User.objects.filter(name__contains=name), 'redir': redir, 'rb': '{{tbl_name}}', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("user/index.html")
            context = Context({'rb': '{{tbl_name}}', 'user': request.user})
            return HttpResponse(template.render(context))
"""

for mod_name, mod_class in inspect.getmembers(users):
    if mod_name in users.__all__:
        template_text = """
{% extends "layout.html" %}
{% load staticfiles %}
{% block content %}
<form role="form" action="{% url 'admin:user:{{tbl_name}}' mod.id %}" method="post">
<table>
    {{content}}
    <tr>
        <td>{{ msg }}</td>
        <td>
            <div class="buttons">
                <input type="submit" value="保存" />
                <input type="reset" value="取消" />
            </div>
        </td>
    </tr>
</table>
</form>
{% endblock %}

{% block topbar %}{% include 'topbar.html' with tb='user_admin' %}{% endblock %}
{% block leftbar %}{% include 'leftbar.html' with tb='user_admin' lb='user' %}{% endblock %}
{% block rightbar %}{% include 'rightbar.html' with tb='user_admin' lb='user' rb='{{tbl_name}}' %}{% endblock %}

{% block css %}
{% include 'parts/input_style.html' %}
<style>
    input.tiny {
        width: 60px;
    }
</style>
{% endblock %}
"""
        template_contet_text = """{% include "parts/input_control.html" with text="{{text}}" name="{{name}}" type="{{type}}" maxlen="{{maxlen}}" value=mod.{{name}} %}"""
        
        tbl_name = mod_class._meta.db_table
        
        url_text += "url(r'^" + tbl_name + "/list/(?P<id>\w+)?$', " + mod_name  + "List.as_view(), name='" + tbl_name + "_list'),url(r'^" + tbl_name + "/(?P<id>\w+)$', " + mod_name  + "View.as_view(), name='" + tbl_name + "'),"

        args_text = ""
        content_text = ""
        for fld in mod_class._meta.get_fields():
            if isinstance(fld, models.CharField):
                args_text += "'" + fld.name + "': forms.CharField(" + ("max_length=" + str(fld.max_length) + "," if (fld.max_length is not None and fld.max_length > 0) else "") + ("required=False," if (fld.null or fld.default == '') else "") + "),"
                content_text += template_contet_text.replace('{{text}}', fld.name).replace('{{name}}', fld.name).replace('{{type}}', 'text').replace("{{maxlen}}", (str(fld.max_length) if (fld.max_length is not None and fld.max_length > 0) else "0"))
            elif isinstance(fld, models.BooleanField):
                args_text += "'" + fld.name + "': forms.BooleanField(required=False),"
                content_text += template_contet_text.replace('{{text}}', fld.name).replace('{{name}}', fld.name).replace('{{type}}', 'checkbox')
            elif isinstance(fld, models.DateTimeField):
                args_text += "'" + fld.name + "': forms.DateTimeField(" + ("required=False," if (fld.null or fld.default is not None ) else "") + "),"
                content_text += template_contet_text.replace('{{text}}', fld.name).replace('{{name}}', fld.name).replace('{{type}}', 'datetime')
            elif isinstance(fld, models.DateField):
                args_text += "'" + fld.name + "': forms.DateField(" + ("required=False," if (fld.null or fld.default is not None ) else "") + "),"
                content_text += template_contet_text.replace('{{text}}', fld.name).replace('{{name}}', fld.name).replace('{{type}}', 'date')
            elif isinstance(fld, models.TextField):
                args_text += "'" + fld.name + "': forms.CharField(" + ("required=False," if (fld.null or fld.default is not None ) else "") + "),"
                content_text += template_contet_text.replace('{{text}}', fld.name).replace('{{name}}', fld.name).replace("{{maxlen}}", (str(fld.max_length) if (fld.max_length is not None and fld.max_length > 0) else "0"))
            elif isinstance(fld, models.IntegerField):
                args_text += "'" + fld.name + "': forms.IntegerField(" + ("required=False," if (fld.null or fld.default is not None ) else "") + "),"
                content_text += template_contet_text.replace('{{text}}', fld.name).replace('{{name}}', fld.name).replace('{{type}}', 'number')
            elif isinstance(fld, models.FloatField):
                args_text += "'" + fld.name + "': forms.FloatField(" + ("required=False," if (fld.null or fld.default is not None ) else "") + "),"
                content_text += template_contet_text.replace('{{text}}', fld.name).replace('{{name}}', fld.name).replace('{{type}}', 'number')
            elif isinstance(fld, models.ForeignKey):
                content_text += '<tr><td>' + fld.name + '：</td><td><a href="{% url "admin:user:' + fld.rel.to._meta.db_table + '" mod.' + fld.name + '.id %}">{{ mod.' + fld.name + '.id }}</a></td></tr>'
        
        view_text += view_class_text.replace('{{cls_name}}', mod_name).replace('{{tbl_name}}', tbl_name).replace('{{args}}', args_text)
        template_file = codecs.open("./admin/templates/user/" + tbl_name + ".html", "w", "utf-8")
        template_file.write(template_text.replace('{{content}}', content_text).replace('{{tbl_name}}', tbl_name))
        template_file.close()

        template2_text = """
{% extends "layout.html" %}
{% load staticfiles %}
{% block content %}
<table style="margin:30px">
    {% for item in list %}
        <tr>
            <td>用户名： </td>
            <td style="min-width: 200px;border:1px solid #C4D9AE;">{{ item.user.name }}</td>
            <td><a href="{% url 'admin:user:{{tbl_name}}' item.user.id %}">查看</a></td>
        </tr>
    {% endfor %}
</table>
{% endblock %}

{% block topbar %}{% include 'topbar.html' with tb='user_admin' %}{% endblock %}
{% block leftbar %}{% include 'leftbar.html' with tb='user_admin' lb='user' %}{% endblock %}
{% block rightbar %}{% include 'rightbar.html' with tb='user_admin' lb='user' rb='{{tbl_name}}' %}{% endblock %}

{% block css %}
{% include 'parts/input_style.html' %}
{% endblock %}
"""
        template2_file = codecs.open("./admin/templates/user/" + tbl_name + "_list.html", "w", "utf-8")
        template2_file.write(template2_text.replace('{{tbl_name}}', tbl_name))
        template2_file.close()

url_text += "]"
url_file = codecs.open("./admin/urls/user.py", "w", "utf-8")
url_file.write(url_text)
url_file.close()

view_file = codecs.open("./admin/views/user.py", "w", "utf-8")
view_file.write(view_text)
view_file.close()
