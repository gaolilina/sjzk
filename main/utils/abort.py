from django.http import HttpResponse


class AbortException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


# noinspection PyMethodMayBeStatic
class AbortExceptionHandler(object):
    """处理AbortException的中间件"""

    def process_exception(self, request, exception):
        if isinstance(exception, AbortException):
            return HttpResponse(exception.message, status_code=exception.code)


def abort(code, message=''):
    """终止其他过程的执行并抛出一个用于返回HTTP响应的异常"""

    raise AbortException(code, message)
