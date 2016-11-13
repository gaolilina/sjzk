创易项目说明
============
本项目利用[Git](https://git-scm.com/)进行版本控制，基于[Python 3.4+](https://www.python.org/)、[Django 1.9](https://www.djangoproject.com)实现，此外使用到了[Pillow](https://pypi.python.org/pypi/Pillow/)进行图片处理。

当前服务器端的主要职责为实现核心逻辑并向APP端提供对应接口。

Django入门可参考[Django Tutorials](https://docs.djangoproject.com/en/1.9/intro/)，详细文档可参考[Django Documentation](https://docs.djangoproject.com/en/1.9/)。

## 基本配置
项目的配置文件为`ChuangYi.settings`，具体说明可以参考[相关文档](https://docs.djangoproject.com/en/1.9/ref/settings/)。实际部署时可能修改的配置包括debug开关、数据库、上传文件目录等。

### 数据库配置
当前的实现不依赖任何特定数据库，本地测试时可直接使用sqlite，在实际部署中可以选择MySQL或PostgreSQL（并安装相应的驱动）。

### 上传文件保存目录
`UPLOADED_URL`为已上传文件的URL前缀，`UPLOADED_ROOT`为保存上传文件的文件系统路径。此外需要在nginx中进行相应配置才能正常访问这些文件。

## URL配置
本项目使用RESTful风格的API命名，并按照Django惯例以`/`结尾，具体可以参考[RESTful API 设计指南](http://www.ruanyifeng.com/blog/2014/05/restful_api.html)。关于Django的URL配置可以参考[相关文档](https://docs.djangoproject.com/en/1.9/topics/http/urls/)。

项目按照逻辑将URL配置划分为多个模块。根级URL配置为`main.urls`，配置各个功能模块对应的URL前缀。各个功能模块级的URL配置为`main.urls.*`，配置具体URL与控制器的映射。

## 数据库模型
项目按照逻辑将各个数据库模型划分为多个模块，均位于`main.models`中。如果要添加新模型，务必将添加的模型类名称加入对应模块的`__all__`列表中。

如果要添加新模块，务必在`main.models`中import新添加的模块即其所包含的模型。关于Django的模型可以参考[相关文档](https://docs.djangoproject.com/en/1.9/topics/db/models/)。

## 控制器
控制器为实现具体业务逻辑的载体（在Django中成为view)。项目按照逻辑将各个数据库模型划分为多个模块，均位于`main.views`中。关于Django的控制器可以参考[此处列出的目录](https://docs.djangoproject.com/en/1.9/#the-view-layer)。

当前控制器的实现均继承自`django.views.generic.View`，在继承类中实现get/post/delete等方法，以响应同一个URL、不同的方式的HTTP请求。可以使用响应的装饰器简化某些操作流程。

## Helper功能
为了简化某些重复性工作，本项目中实现了一些Helper功能，它们位于`main.utils`之中。

### 装饰器
项目实现了一些装饰器以简化控制器方法中的一些重复工作，它们位于`main.utils.decorators`。目前以下几个装饰器：`require_token`、`require_verficication`、`validate_args`、`fetch_object`。

#### `require_token`
表示调用该方法时必须提供用户身份。调用该装饰器装饰的方法时，会检查随HTTP请求发送的用户令牌，若令牌有效，获取到的用户信息可供被装饰方法执行时使用，否则返回401响应。用户令牌作为HTTP请求头`X-User-Token`进行传递。

#### `require_verification`
表示只有进行过实名认证的用户才可以调用该方法。该装饰器应配合`require_token`使用并被`require_token`装饰。

#### `validate_args`
调用被装饰的方法时，根据该装饰器的表单验证模型参数对HTTP请求参数进行验证，若验证无误则继续执行被装饰的方法，否则返回400响应。

该装饰器利用了Django的表单模型的验证功能，所需参数是一个“HTTP请求参数名/Django表单字段”字典，具体可参考[此处列出的目录](https://docs.djangoproject.com/en/1.10/#forms)。

#### `fetch_object`
使用该装饰器装饰某个方法时，根据HTTP请求中类似`xxx_id`的参数从数据库中提前取出相关模型实例，若实例存在则将其作为关键字参数`xxx`传入被装饰的方法，否则返回404响应。若HTTP请求中没有`xxx_id`的参数，则忽略。

### 保存上传图片
可以调用`main.util.save_uploaded_image`方法将上传的图片按处理时间进行命名，并保存在相对于`UPLOADED_ROOT`下的`%Y/%m/%d`路径中，图片将转换为质量90的JPEG格式。若无错误发生则返回图片的相对路径，否则返回None。

### 返回特定状态码的响应
可以调用`main.util.abort`方法返回包含某个状态码的响应，并可同时返回可选信息。

## 部署
建议使用nginx+Gunicorn进行部署，相关配置可以参考[How to use Django with Gunicron](https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/gunicorn/)。
