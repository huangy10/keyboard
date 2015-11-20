import json
import uuid

from django.contrib.auth import get_user_model
from django.http import JsonResponse

# Create your views here.


def request_account(request):
    """ New user send request for a account
    """
    new_account = get_user_model().objects.create()
    new_account.username = str(new_account.id)
    password = str(uuid.uuid4())
    new_account.set_password(password)
    new_account.profile.device_type = request.POST.get('device_type', '')
    new_account.save()
    return JsonResponse({
        'success': True,
        'data': {
            'username': new_account.username,
            'password': password
        }
    })