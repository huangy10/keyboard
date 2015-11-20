import json
import datetime

from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth

from .models import Emoticon, EmoticonType
from .utils import version_compare, parse_user_info
from .http import XAccelRedirectResponse
from Statistics.models import EmoticonUsage, EmoticonUpdate
# Create your views here.


@csrf_exempt
@parse_user_info
def check_update(request):
    """ User send request to check if they need to update their emoticons

     You should update the following data:
      :keyword version_info - An array serialized to json containing all the emoticon version info,
        this dict is organized as follows:
        [{
            'emoticon_type_id': 'some_id',
            'emoticon_version_no: no,
            'emoticons': {
                'code': 'version_no',
            },
        },]
      :return update_list - A JSON response containing all the emoticons which need to be updated,
        its format is organized as follows:
        {
            'success': True or False,
            'update_list': [{
                'emoticon_type_id': 'related_id',
                'version_no: latest_no,
                'order_weight':
                'name':
                'emoticons': [{
                    'code': 'emoticon_code',
                    'version_no': 'latest_emoticon_no',   -- omitted for delete
                    'order_weight': 'order_weight'
                    'icon_url': 'url_for_downloading',  -- omitted for delete
                    'description': 'blabla',  -- omitted for delete
                    'operation': 'add/change/delete'
                },]
            },],
            'deleted_types': ['type_id', ]
        }
    """
    # Get the json data
    data = json.loads(request.body)
    print data[u'version_info']
    return JsonResponse(version_compare(data[u'version_info']))


@csrf_exempt
@parse_user_info
def all_emoticon_types(request):
    """ Fetch all available emoticon types

    This view takes no extra arguments other than identification arguments, it provides all the available emoticons'
     basic information.
     :return {
        'success': True
        'emoticon_types': [{
            'id': 'id',
            'name': 'type_name',
            'version_no': 'version_no',
            'order_weight': 'order_weight',
            'time_mark_start_hour': 'hour',
            'time_mark_start_min': 'min',
            'time_mark_end_hour': 'hour',
            'time_mark_end_min': 'min'
            }, ]
        }
    """
    result = EmoticonType.objects.filter(is_active=True).values(
        'id', 'order_weight', 'name', 'version_no',
        'time_mark_start_hour', 'time_mark_start_min', 'time_mark_end_hour', 'time_mark_end_min')
    return JsonResponse({
        'success': True,
        'emoticon_types': list(result)
    })


@csrf_exempt
@parse_user_info
def usage_report_types(request):
    """ Usage of emoticons will be send to the server for analysis
     :keyword usage {
        'emoticon_code': 'code',
        'version_no': 'version_no'
        'use_time': 'YY-MM-DD HH:MM:SS'
        }
    """
    data = json.loads(request.body)
    try:
        e = Emoticon.objects.get(code=data['emoticon_code'],
                                 version_no=int(data['version_no']),)
    except ObjectDoesNotExist:
        return JsonResponse(dict(success=False, reason='Emoticon Not Found'))
    except MultipleObjectsReturned:
        return JsonResponse(dict(success=False, reason='Internal Error Found'))
    except ValueError:
        return JsonResponse(dict(success=False, reason='Format Error with Posted Data'))
    EmoticonUsage.objects.create(use_time=datetime.datetime.strptime(data['use_time'], "%Y-%m-%d %H:%M:%S"),
                                 emoticon_used=e,
                                 user=request.user)
    return JsonResponse(dict(success=True))


def fetch_emoticon(request, emoticon_code, version_no):
    """ Clients send request to this url to get the emoticon file
    """
    try:
        e = Emoticon.objects.get(code=emoticon_code, version_no=version_no)
    except ObjectDoesNotExist:
        raise Http404
    if not request.user.is_authenticated():
        username = request.GET['username']
        password = request.GET['passwd']
        user = auth.authenticate(username=username, password=password)
        if user is None:
            return JsonResponse(dict(success=False, reason='Permission Denied'))
        else:
            auth.login(request, user)
    EmoticonUpdate.objects.create(update_time=timezone.now(),
                                  emoticon=e,
                                  user=request.user)

    file_path = settings.MEDIA_URL + e.icon.name
    ext = e.icon.name.split(".")[-1]
    file_name = "{0}.{1}".format(e.code, ext)
    return XAccelRedirectResponse(file_path, file_name)


def get_thumbnail_for_type(request, type_id):
    try:
        e_type = EmoticonType.objects.get(id=type_id)
    except:
        raise Http404

    if not request.user.is_authenticated():
        username = request.GET['username']
        password = request.GET['passwd']
        user = auth.authenticate(username=username, password=password)
        if user is None:
            return JsonResponse(dict(success=False, reason='Permission Denied'))
        else:
            auth.login(request, user)
    e = Emoticon.objects.filter(e_type=e_type, is_published=True).order_by('-order_weight').first()
    file_path = settings.MEDIA_URL + e.icon.name
    ext = e.icon.name.split(".")[-1]
    file_name = "{0}.{1}".format(e.code, ext)
    return XAccelRedirectResponse(file_path, file_name)