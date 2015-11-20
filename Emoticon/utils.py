# coding=utf-8
import uuid
import json

from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from .models import EmoticonType, Emoticon


def parse_user_info(method):
    """ This decorator parse user info from the request, and log it in automatically

    You are free to assume the user is logged in after this.
    """
    def wrapper(request, **kwargs):
        print request.body
        if request.user.is_authenticated():
            # If the current user is already logged in, skip the authentication below
            return method(request, **kwargs)
        user = None
        data = json.loads(request.body)
        if 'username' in data and 'password' in data:
            user = auth.authenticate(username=data['username'], password=data['password'])
        if user is not None:
            auth.login(request, user)
            return method(request, **kwargs)
        else:
            return JsonResponse(dict(success=False, reason='Permission Denied'))

    return wrapper


def version_compare(version_info):
    """ This utility function accept the version info dict provided by the user, and response with a dict containing
     all the update information. Check `check_update` in views.py for details.
    """
    update_list = []
    deleted_types = []
    for version_dict in version_info:
        update_list_in_this_type = []
        try:
            # First, find out the related emoticon types
            e_type = EmoticonType.objects.get(id=version_dict['emoticon_type_id'], is_active=True)
        except ObjectDoesNotExist:
            # If no active emoticon types are found, then the related type should be considered as deleted
            deleted_types.append(version_dict['emoticon_type_id'])
            continue
        except KeyError:
            continue

        # Then check the version No.
        version_no = version_dict['emoticon_version_no']
        if e_type.version_no <= version_no:
            # if this type is the latest, then go on for next type
            continue

        # Then check all the emoticons belong to this type
        emoticons = version_dict['emoticons']
        e_reference = e_type.version_synchronization    # 取出该类别的最新版本信息，开始比对
        for code in e_reference.keys():
            if code in emoticons and emoticons[code] < e_reference[code]:
                emoticon = Emoticon.objects.get(code=code, version_no=e_reference[code])
                update_list_in_this_type.append({
                    'code': emoticon.code,
                    'version_no': emoticon.version_no,
                    'order_weight': emoticon.order_weight,
                    'icon_url': emoticon.icon.url,
                    'description': emoticon.description,
                    'operation': 'change'
                })
            elif code not in emoticons:
                emoticon = Emoticon.objects.get(code=code, version_no=e_reference[code])
                update_list_in_this_type.append({
                    'code': emoticon.code,
                    'version_no': emoticon.version_no,
                    'order_weight': emoticon.order_weight,
                    'icon_url': emoticon.icon.url,
                    'description': emoticon.description,
                    'operation': 'add'
                })
        for code in (set(emoticons.keys()) - set(e_reference.keys())):
            update_list_in_this_type.append({
                'code': code,
                'operation': 'delete'
            })

        update_list.append({
            'emoticon_type_id': e_type.id,
            'version_no': e_type.version_no,
            'order_weight': e_type.order_weight,
            'name': e_type.name,
            'time_mark_start_hour': e_type.time_mark_start_hour,
            'time_mark_end_hour': e_type.time_mark_end_hour,
            'time_mark_start_min': e_type.time_mark_start_min,
            'time_mark_end_min': e_type.time_mark_end_min,
            'emoticons': update_list_in_this_type
        })

    result = {
        'success': True,
        'update_list': update_list,
        'deleted_types': deleted_types
        }
    return result