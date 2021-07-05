import os
import subprocess

import redis
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.authentication import TokenAuthentication
from drf_yasg2.utils import swagger_auto_schema

from common.parse_ui_testCase import format_ui_case
from common.redis_pool import redis_pool
from common.regular_ls import REGEX_PY_MODEL, REGEX_FOLD
from rest_framework.views import APIView
from automated_testing.common.api_response import JsonResponse
from basic_configuration.settings import AUTOMATED_UI_TESTING_CONF
import re


class FolderManagerView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = []
    create_type_ls = ('pymodel', 'folder', 'excel')

    @swagger_auto_schema(
        operation_summary='创建 文件夹&py文件',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'create_type': openapi.Schema(type=openapi.TYPE_STRING, description='创建类型 {}'.format("/".join(create_type_ls))),
                'file_name': openapi.Schema(type=openapi.TYPE_STRING, description='创建的文件名称'),
                'file_path': openapi.Schema(type=openapi.TYPE_STRING, description='创建路径 创建文件的上层路径 不带文件名'),
            }))
    def post(self, request):
        """创建 文件夹&py文件"""
        data = JSONParser().parse(request)
        create_type = data['create_type']
        if create_type not in self.create_type_ls:
            return JsonResponse(code="999998", msg="参数错误!")
        file_name = data['file_name']
        file_path = data['file_path']

        file_path = os.path.join(file_path, file_name)   # 创建的文件路径

        if create_type == 'pymodel' or create_type == 'excel':
            if create_type == 'pymodel':
                if '.py' not in file_name or not re.compile(REGEX_PY_MODEL).search(file_name):
                    return JsonResponse(code="999998", msg="文件名非法!")
            else:
                if '.xlsx' not in file_name or re.compile(REGEX_FOLD).search(file_name):
                    return JsonResponse(code="999998", msg="文件名非法!")
            redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
            if redis_conn.hget('ui_case_ls_path', file_name):
                return JsonResponse(code="999998", msg="修改失败!文件重名!")
            if not os.path.isfile(file_path):
                os.mknod(file_path)
            else:
                return JsonResponse(code="999998", msg="重复创建!已存在{}文 件!".format(file_name))
        elif create_type == 'folder':
            if not re.compile(REGEX_PY_MODEL).search(file_name):
                return JsonResponse(code="999998", msg="文件名非法!")
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            else:
                return JsonResponse(code="999998", msg="重复创建!已存在{}文件!".format(file_name))
        return JsonResponse(code="999999", msg="创建成功!")

    @swagger_auto_schema(
        operation_summary='修改 文件夹&py文件名称',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'modify_type': openapi.Schema(type=openapi.TYPE_STRING, description='修改类型 {}'.format("/".join(create_type_ls))),
                'file_path': openapi.Schema(type=openapi.TYPE_STRING, description='文件路径 当前文件的路径 带文件名'),
                'new_name': openapi.Schema(type=openapi.TYPE_STRING, description='新名称'),
            }))
    def put(self, request):
        data = JSONParser().parse(request)
        modify_type = data['modify_type']
        if modify_type not in self.create_type_ls:
            return JsonResponse(code="999998", msg="参数错误!")
        file_name = data['new_name']
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        if redis_conn.hget('ui_case_ls_path', file_name):
            return JsonResponse(code="999998", msg="修改失败!文件重名!")

        file_path = data['file_path']
        new_file_path = os.path.join('/'.join(file_path.split('/')[0: -1]), file_name)

        if modify_type == 'pymodel' or modify_type == 'excel':
            if '.py' not in file_name or not re.compile(REGEX_PY_MODEL).search(file_name):
                return JsonResponse(code="999998", msg="文件名非法!")
            else:
                if '.xlsx' not in file_name or re.compile(REGEX_FOLD).search(file_name):
                    return JsonResponse(code="999998", msg="文件名非法!")
            if not os.path.isfile(file_path):
                return JsonResponse(code="999998", msg="不存在{}文件!请重新创建!".format(file_path.split('/')[-1]))
            else:
                os.rename(file_path, new_file_path)
        elif modify_type == 'folder':
            if not re.compile(REGEX_PY_MODEL).search(file_name):
                return JsonResponse(code="999998", msg="文件名非法!")
            if not os.path.exists(file_path):
                return JsonResponse(code="999998", msg="不存在{}文件!请重新创建!".format(file_path.split('/')[-1]))
            else:
                os.rename(file_path, new_file_path)
        return JsonResponse(code="999999", msg="修改成功!")











