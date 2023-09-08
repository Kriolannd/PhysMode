import json

from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

mp = apps.get_app_config("physmode").mp


@require_POST
@csrf_exempt
def switch(request):
    mp.switch()
    return HttpResponse("OK")


@require_POST
@csrf_exempt
def set_params(request):
    data = json.loads(request.body)

    mp.set_trefr(data.get("t_refr"))
    mp.set_distortion_params(data.get("sigma"), data.get("alpha"))

    return HttpResponse("OK")
