import json

from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

mp = apps.get_app_config("physmode").mp


def switch(request):
    mp.switch()
    return HttpResponse("OK")


@csrf_exempt
def set_params(request):
    if request.method != "POST": return

    data = json.loads(request.body)

    mp.set_trefr(data.get("t_refr"))
    mp.set_distortion_params(data.get("sigma"), data.get("alpha"))

    return HttpResponse("OK")
