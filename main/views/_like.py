from django import forms
from django.http import JsonResponse
from django.views.generic import View
from main.responses import *

from main.models import User, Team
from main.utils.decorators import validate_args, require_token, fetch_object




