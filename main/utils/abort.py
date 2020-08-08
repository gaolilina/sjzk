from django.http import HttpResponse
from util.code import error

class AbortException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


# noinspection PyMethodMayBeStatic
class AbortExceptionHandler(object):
    """处理AbortException的中间件"""

    def process_exception(self, request, exception):
        if isinstance(exception, AbortException):
            r = HttpResponse(exception.message)
            r.status_code = exception.code
            r.code = set_code(exception.code)

            return r


def abort(code, message=''):
    """终止其他过程的执行并抛出一个用于返回HTTP响应的异常"""

    raise AbortException(code, message)


def set_code(code):
    '''
    400  参数问题  	error.LACK_PARAM
    401  证书未授权/用户对象未找到  	error.NO_USER
    403  权限问题   禁止	error.NO_PERMISSION
    404  路径问题/对象未找到	error.NOT_FOUND
    :param code:
    :return:
    '''
    if code == 200:
        return 0
    elif code == 400:
        return error.LACK_PARAM
    elif code == 401:
        return error.NO_USER
    elif code == 403:
        return error.NO_PERMISSION
    elif code == 404:
        return error.NOT_FOUND
    elif code == 500:
        return error.SERVER_ERRO
    else:
        return -100