# -*- coding: utf-8 -*-
import json

from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from django.db import transaction

from account_system.tools import get_real_name
from system_settings.models import *
from system_settings.serializers import TaskSerializerQuery, TaskSerializerAdd
from system_settings.taskjob.singleton import scheduler
from system_settings.taskjob.task_base_service import TaskBaseService
from system_settings.tools import error_response, success_response

from zy_api_testing.tools import deal_time_task

# 定时任务启动
scheduler.start()
add_job = TaskBaseService()
try:
    add_job.add_jobs()
except Exception as e:
    pass


class TaskView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='定时任务 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='job_name', in_=openapi.IN_QUERY, description='任务名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='job_status', in_=openapi.IN_QUERY, description='任务状态', type=openapi.TYPE_STRING),
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='id ,单查时传入', type=openapi.TYPE_INTEGER),
        ])
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
            id = request.GET.get('id', None)
            job_name = request.GET.get('job_name')
            job_status = request.GET.get('job_status')
            aQ = Q()
            if job_name:  # 多字段筛选
                aQ.add(Q(job_name=job_name), Q.AND)
            if job_status:
                aQ.add(Q(job_status=job_status), Q.AND)
            if id:
                task_obj, msg = TaskBaseService.get_task_by_id(id)
                if not task_obj:
                    return error_response(msg='查询任务不存在')
                task_serialize = TaskSerializerQuery(task_obj)
                data = task_serialize.data
            else:
                data = TaskBaseService.get_job_list(aQ, page, page_size)
            return success_response(data=data, msg='查询成功')
        except Exception as e:
            return error_response(msg=str(e))

    @swagger_auto_schema(
        operation_summary='定时任务 新增',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'job_type': openapi.Schema(type=openapi.TYPE_STRING, description='任务类型ui/api'),
                'job_name': openapi.Schema(type=openapi.TYPE_STRING, description='任务名称'),
                'environment': openapi.Schema(type=openapi.TYPE_INTEGER, description='环境id'),
                'performMachine': openapi.Schema(type=openapi.TYPE_INTEGER, description='执行机id ui场景专用'),
                'test_config_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试配置id列表'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
                'mails': openapi.Schema(type=openapi.TYPE_STRING, description='邮箱 多个使用,隔开'),
                'cron_expression': openapi.Schema(type=openapi.TYPE_STRING, description='执行时间  "%Y-%m-%d %H:%M:%S"格式'),
                'execute_type': openapi.Schema(type=openapi.TYPE_STRING, description='执行周期类型 0,1,2,3   立即执行/每天定点执行/每周定点执行/每月定点执行'),
                'execute_day': openapi.Schema(type=openapi.TYPE_STRING, description='执行周期参数  具体某周/日'),
            }))
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            data['method'] = 'selfsetTimeTask'
            data['end_cron_expression'] = 'pass'  # 占位使用
            data['job_status'] = 1
            data['create_user'] = get_real_name(request)
            try:
                data['test_config'] = json.dumps(data.get('test_config_id'))
            except Exception as e:
                return error_response("测试环境id错误！！")
            task_serializer = TaskSerializerAdd(data=data)
            if task_serializer.is_valid():

                save_data = task_serializer.save()
                if save_data.execute_type not in [0, '0']:
                    TaskBaseService.start_task(save_data.id)
                else:  # 立即执行
                    try:
                        rep = deal_time_task(save_data.id, data['job_type'])
                        print(rep)
                    except Exception as e:
                        print(str(e))
                return success_response(data='', msg="成功")
            else:
                return error_response(msg=task_serializer.errors)
        except Exception as e:
            return error_response('失败！！')

    @swagger_auto_schema(
        operation_summary='定时任务 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='任务id'),
                'job_type': openapi.Schema(type=openapi.TYPE_STRING, description='任务类型0/1 ui/api'),
                'job_name': openapi.Schema(type=openapi.TYPE_STRING, description='任务名称'),
                'environment': openapi.Schema(type=openapi.TYPE_INTEGER, description='环境id'),
                'test_config_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试配置id列表'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
                'mails': openapi.Schema(type=openapi.TYPE_STRING, description='邮箱 多个使用,隔开'),
                'cron_expression': openapi.Schema(type=openapi.TYPE_STRING, description='执行时间  "%Y-%m-%d %H:%M:%S"格式'),
                'execute_type': openapi.Schema(type=openapi.TYPE_STRING, description='执行周期类型 0,1,2,3   立即执行/每天定点执行/每周定点执行/每月定点执行'),
                'execute_day': openapi.Schema(type=openapi.TYPE_STRING, description='执行周期参数  具体某周/日'),
            }))
    def put(self, request):
        data = JSONParser().parse(request)
        data['method'] = 'selfsetTimeTask'
        data['end_cron_expression'] = 'pass'  # 占位使用
        pk = data.get('id')
        if not pk:
            return error_response(msg='id is None')
        task_obj = TaskControl.objects.filter(id=pk).first()
        try:
            data['test_config'] = eval(data.get('test_config_id'))
        except Exception as e:
            return error_response("测试环境id错误！！")
        task_serializer = TaskSerializerAdd(instance=task_obj, data=data)
        if task_serializer.is_valid():
            save_data = task_serializer.save()
            if save_data.state == 1:
                TaskBaseService.stop_task(save_data.id)
                TaskBaseService.start_task(save_data.id)
            return success_response(data='', msg="成功")
        else:
            return error_response(msg=task_serializer.errors)

    @swagger_auto_schema(
        operation_summary='定时任务 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的定时任务id列表 ')
            }))
    def delete(self, request):
        """定时任务 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data['ids']
                for id in delete_ids:
                    task_obj = TaskControl.objects.filter(id=id).first()
                    if task_obj.state == 2:
                        TaskBaseService.stop_task(task_obj.id)
                    if task_obj:
                         task_obj.delete()
                    else:
                        return error_response(msg="数据错误!")
        except Exception as e:
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")


class ControlTask(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='定时任务 启动/停止',
        manual_parameters=[
            openapi.Parameter(name='control_type', in_=openapi.IN_QUERY, description='stop/start', type=openapi.TYPE_STRING),
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='任务id', type=openapi.TYPE_INTEGER),
        ])
    def get(self, request):
        try:
            with transaction.atomic():
                id = request.GET.get('id', None)
                control_type = request.GET.get('control_type', None)
                if id:
                    if control_type == 'stop':
                        try:
                            flg, msg = TaskBaseService.stop_task(id)
                        except Exception as e:
                            raise Exception('任务执行中，请稍候')
                    elif control_type == 'start':
                        task_obj = TaskBaseService.get_task_by_id(id)[0]
                        if not task_obj.end_cron_expression:  # 立即执行
                            try:
                                task_obj.job_status = 1
                                task_obj.execution_status = 1
                                task_obj.save()
                                flg = True

                                rep = deal_time_task(task_obj.id, task_obj.job_type)
                                print(rep)
                            except Exception as e:
                                print(str(e))
                        else:
                            flg, msg = TaskBaseService.start_task(id)

                    else:
                        return error_response(msg='control_type错误!')

                    if flg:
                        return success_response(data='', msg='操作成功')
                    else:
                        return error_response(msg=msg)
                else:
                    return error_response(msg='id错误!')
        except Exception as e:
            return error_response(msg=str(e))

