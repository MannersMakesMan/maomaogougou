import json
import os
from rest_framework.authtoken.models import Token

from account_system.models import PermissionViewResources


def get_real_name(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    try:
        token_obj = Token.objects.get(key=token)
        real_name = token_obj.user.Real_name
        if not real_name:
            real_name = token_obj.user.username
    except:
        real_name = 'default'
    return real_name


def save_permissionview_resource():
    root_path = os.getcwd()
    json_path = os.path.join(root_path, 'account_system', 'views', 'permissionview_resources.json')
    with open(json_path, encoding='utf-8') as f:
        line = f.read()
        d = json.loads(line)['RECORDS']
    try:
        PermissionViewResources.objects.all().delete()
        for permissionview_resources_dic in d:
            permissionview_resources_dic['id'] = str(permissionview_resources_dic['id'])
            permissionview_resources_dic['super_resource_id'] = str(
                permissionview_resources_dic['super_resource_id']) if str(
                permissionview_resources_dic['super_resource_id']) else None
            permissionview_resources_dic['sort_num'] = str(permissionview_resources_dic['sort_num']) if str(
                permissionview_resources_dic['sort_num']) else None
            if not PermissionViewResources.objects.filter(name=permissionview_resources_dic['name']):
                PermissionViewResources.objects.create(**permissionview_resources_dic)
    except Exception as e:
        pass
