from django.http import HttpResponse
from django.http import HttpResponseNotModified
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound

Http200 = HttpResponse
Http304 = HttpResponseNotModified
Http400 = HttpResponseBadRequest
Http403 = HttpResponseForbidden
Http404 = HttpResponseNotFound


class Http401(HttpResponse):
    status_code = 401


__all__ = ['Http200', 'Http304', 'Http400', 'Http401', 'Http403', 'Http404']
