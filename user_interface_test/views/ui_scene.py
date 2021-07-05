# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from account_system.tools import get_real_name
from automatic_ui.ui_script_execution import ui_script_execution
from system_settings.models import DataDictionary, Dataexplain, TaskControl
from system_settings.tools import error_response, success_response
from test_exe_conf.serializers import ApiTestReportSerializers, UiTestReportSerializers
from user_interface_test.models import CommonParams, TestAppModel, UiTestScene, TestCase, TestCaseData, UiSceneParams, \
    UiSceneTestCaseIndex
from user_interface_test.serializers import UiTestParamsSerializerQuery, UiTestParamsSerializerAdd, \
    TestModelSerializerAdd, TestModelSelectSerializerQuery, TestSceneSerializerQuery, \
    TestSceneSerializerAdd, TestSceneParamsSerializer
from user_interface_test.tools import get_one_test_scene_data
from zy_api_testing.tools import DelException, api_list_query


class TestSceneQueryView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试场景 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='model_name', in_=openapi.IN_QUERY, description='模块名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='fun_name', in_=openapi.IN_QUERY, description='功能名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='scene_name', in_=openapi.IN_QUERY, description='场景名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='场景id', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            total, obm = api_list_query(data, page, page_size, UiTestScene, 'id',
                                        ['model_name', 'fun_name', 'scene_name', 'id'])
            try:
                test_scene_serialize = TestSceneSerializerQuery(obm, many=True)
                return_data = test_scene_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as _:
            return error_response('失败!')


class TestSceneAdd(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试场景 新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名'),
                'fun_name': openapi.Schema(type=openapi.TYPE_STRING, description='功能名'),
                'scene_name': openapi.Schema(type=openapi.TYPE_STRING, description='场景名'),
                'scene_desc': openapi.Schema(type=openapi.TYPE_STRING, description='场景描述'),
                'test_case_ids': openapi.Schema(type=openapi.TYPE_ARRAY, description='用例id列表', items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                    'test_case_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试用例id'),
                    'test_case_index': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试用例排序值'),
                })),
                'reMark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                data['update_user'] = get_real_name(request)
                test_case_ids = data.pop('test_case_ids')
                test_scene_serializer = TestSceneSerializerAdd(data=data)
                if test_scene_serializer.is_valid():
                    data = test_scene_serializer.save()
                    for i in test_case_ids:
                        i['scene_id'] = data.id
                        m = UiSceneTestCaseIndex(**i)
                        m.save()
                    return success_response(data=model_to_dict(data), msg='新增测试场景信息成功！')
                else:
                    return error_response(msg=test_scene_serializer.errors)
        except Exception as _:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='测试场景 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='场景id'),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名'),
                'fun_name': openapi.Schema(type=openapi.TYPE_STRING, description='功能名'),
                'scene_name': openapi.Schema(type=openapi.TYPE_STRING, description='场景名'),
                'scene_desc': openapi.Schema(type=openapi.TYPE_STRING, description='场景描述'),
                'test_case_ids': openapi.Schema(type=openapi.TYPE_ARRAY, description='用例id列表', items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                    'test_case_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试用例id'),
                    'test_case_index_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试用例排序 id 无此值进行创建'),
                    'test_case_index': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试用例排序值'),
                })),
                'reMark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def put(self, request):
        """测试场景 修改"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                try:
                    data['update_user'] = get_real_name(request)
                except:
                    pass
                id = data.get('id')
                scene_obj = UiTestScene.objects.filter(id=id)
                if not scene_obj:
                    return error_response('id错误')
                test_case_ids = data.pop('test_case_ids')
                test_scene_serializer = TestSceneSerializerAdd(instance=scene_obj.first(), data=data)
                if test_scene_serializer.is_valid():
                    return_data = test_scene_serializer.save()
                    test_case_index_ids = [int(i.get('test_case_index_id', '')) for i in test_case_ids if i.get('test_case_index_id', '')]
                    case_index_objs = UiSceneTestCaseIndex.objects.filter(scene_id=id)
                    # 场景中不存在的测试用例 进行删除 级联删除测试数据
                    for case_index_obj in case_index_objs:
                        if case_index_obj.id not in test_case_index_ids:
                            scene_param_objs = UiSceneParams.objects.filter(test_case_index_id=case_index_obj.id)
                            for scene_param_obj in scene_param_objs:
                                scene_param_obj.delete()
                            case_index_obj.delete()

                    for i in test_case_ids:
                        # 不带test_case_index_id为新数据 进行存贮
                        i['scene_id'] = return_data.id
                        index_id = i.get("test_case_index_id", "")
                        if not index_id:
                            m = UiSceneTestCaseIndex(**i)
                            m.save()
                        else:
                            m = UiSceneTestCaseIndex.objects.get(id=int(index_id))
                            m.test_case_index = i['test_case_index']
                            m.test_case_id = i['test_case_id']
                            m.save()
                    return success_response(data=model_to_dict(return_data), msg='修改测试场景成功！')
                else:
                    return error_response(msg=test_scene_serializer.errors)
        except Exception as e:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='测试场景 单删群删',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的测试场景id列表 ')
            }))
    def delete(self, request):
        """测试场景 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data['ids']
                for id in delete_ids:
                    time_tast_objs = TaskControl.objects.filter(job_type=1, job_id=id)
                    if not time_tast_objs:
                        test_scene = UiTestScene.objects.filter(id=id).first()
                        if test_scene:
                            for i in UiSceneTestCaseIndex.objects.filter(scene_id=int(id)):
                                for j in UiSceneParams.objects.filter(test_case_index_id=i.id):
                                    j.delete()
                                i.delete()
                            test_scene.delete()
                        else:
                            return error_response(msg="数据错误!")
                    else:
                        return error_response(msg="关联定时任务 无法删除!")
        except Exception as _:
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")

    @swagger_auto_schema(
        operation_summary='测试场景 单查',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING),
                           openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='场景id',
                                             type=openapi.TYPE_INTEGER),
                           ],
    )
    def get(self, request):
        scene_id = request.GET.get("id")
        return_data = {}
        try:
            scene_obj = UiTestScene.objects.get(id=int(scene_id))
            scene_data_serializer = TestSceneSerializerQuery(scene_obj)
            return_data["scene_data"] = scene_data_serializer.data
        except Exception as _:
            return error_response(msg="无此场景数据!")
        test_case_index_objs = UiSceneTestCaseIndex.objects.filter(scene_id=int(scene_id)).order_by("test_case_index")
        try:
            return_data['test_case_ls'] = []
            for test_case_index_obj in test_case_index_objs:
                test_case_obj = TestCase.objects.get(id=int(test_case_index_obj.test_case_id))

                return_data['test_case_ls'].append({"test_case_index_id": test_case_index_obj.id,
                                                    "test_case_id": test_case_obj.id,
                                                    "case_name": test_case_obj.case_name,
                                                    "test_case_index": test_case_index_obj.test_case_index})

        except Exception as _:
            return error_response(msg="场景数据异常!")
        return success_response(data=return_data, msg="成功")


class TestSceneData(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试场景-测试用例 数据查询',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING),
                           openapi.Parameter(name='test_case_index_id', in_=openapi.IN_QUERY, description='测试用例排序id',
                                             type=openapi.TYPE_INTEGER),
                           ],
    )
    def get(self, request):
        test_case_index_id = request.GET.get("test_case_index_id")
        try:
            with transaction.atomic():
                try:
                    case_index_obj = UiSceneTestCaseIndex.objects.get(id=int(test_case_index_id))
                except Exception as _:
                    return error_response(msg="此测试用例未被关联")
                scene_param_objs = UiSceneParams.objects.filter(test_case_index_id=int(test_case_index_id))
                # 查询 场景下 此用例 是否有具体参数数据
                is_need_value = 0
                # 用例下是否具有参数
                case_id = case_index_obj.test_case_id
                table_header = []
                step_ids = []
                if scene_param_objs:
                    # 具有历史参数的数据
                    case_step_objs = TestCaseData.objects.filter(test_case_id=int(case_id)).order_by("sort")
                    all_scene_param = []
                    for scene_param_obj in scene_param_objs:
                        return_param_dic = {}
                        param_dic = eval(scene_param_obj.param_dic)
                        for index, case_step_obj in enumerate(case_step_objs):
                            if case_step_obj.is_need_value:
                                is_need_value = 1
                            elif case_step_obj.is_need_assert:
                                is_need_value = 1
                            else:
                                continue
                            step_desc = case_step_obj.step_desc + "_sort{}".format(index)
                            step_id = case_step_obj.id
                            if step_desc not in table_header:
                                table_header.append(step_desc)
                            if step_id not in step_ids:
                                step_ids.append(step_id)
                            param_value = param_dic.get(str(step_id), "")
                            return_param_dic[step_desc] = param_value
                        all_scene_param.append({"id": scene_param_obj.id, "sort": scene_param_obj.sort, "param_dic": return_param_dic})
                    return_data = {"step_ids": step_ids, "table_header": table_header, "param_info": all_scene_param}

                else:
                    # 无历史参数数据 根据测试用例生成第一条默认数据
                    # 测试场景下 单用例的 参数字典 以步骤id作为键名
                    case_step_objs = TestCaseData.objects.filter(test_case_id=int(case_id)).order_by("sort")
                    param_dic = {}
                    # 用于返回前端的字典 {步骤描述: 参数值}
                    save_param_dic = {}
                    # 用于存储的字典 {步骤id: 参数值}
                    for index, case_step_obj in enumerate(case_step_objs):
                        if case_step_obj.is_need_value:
                            is_need_value = 1
                            if case_step_obj.func_common_param_id:
                                common_obj = CommonParams.objects.get(id=case_step_obj.func_common_param_id)
                                value = common_obj.param_value
                            else:
                                value = case_step_obj.func_param
                        elif case_step_obj.is_need_assert:
                            is_need_value = 1
                            value = case_step_obj.assert_value
                        else:
                            continue
                        step_desc = case_step_obj.step_desc
                        step_id = case_step_obj.id
                        if step_desc not in table_header:
                            table_header.append(step_desc)
                        if step_id not in step_ids:
                            step_ids.append(step_id)
                        save_param_dic[str(step_id)] = value
                        param_dic[step_desc+"_sort{}".format(index)] = value
                    if param_dic:
                        test_scene_data_obj = UiSceneParams(test_case_index_id=int(test_case_index_id), param_dic=str(save_param_dic), sort=1)
                        test_scene_data_obj.save()
                        return_data = {"step_ids": step_ids, "table_header": table_header, "param_info": [{"id": test_scene_data_obj.id, "sort": 1, "param_dic": param_dic}]}
                    else:
                        return_data = {"step_ids": step_ids, "table_header": table_header, "param_info": []}
                case_index_obj.is_need_param = is_need_value
                case_index_obj.save()
                return success_response(data=return_data, msg="成功")
        except Exception as _:
            return error_response("查询失败")

    @swagger_auto_schema(
        operation_summary='测试场景-测试用例 数据 新增',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING)],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'sort': openapi.Schema(type=openapi.TYPE_STRING, description='数据排序值'),
                'test_case_index_id': openapi.Schema(type=openapi.TYPE_STRING, description='测试用例排序 id'),
                'param_dic': openapi.Schema(type=openapi.TYPE_OBJECT, description='参数字典 {id: 值}', properties={
                }),
            })
    )
    def post(self, request):
        data = JSONParser().parse(request)
        data['param_dic'] = str(data['param_dic'])
        scene_param_serializer = TestSceneParamsSerializer(data=data)
        if scene_param_serializer.is_valid():
            scene_param_serializer.save()
        else:
            return error_response(msg=scene_param_serializer.errors)
        return success_response(msg='success')

    @swagger_auto_schema(
        operation_summary='测试场景-测试用例 数据 修改',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING)],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='测试数据id'),
                'param_dic': openapi.Schema(type=openapi.TYPE_OBJECT, description='参数字典 {id: 参数值}', properties={
                }),
            })
    )
    def put(self, request):
        data = JSONParser().parse(request)
        data['param_dic'] = str(data['param_dic'])
        try:
            scene_param_obj = UiSceneParams.objects.get(id=int(data['id']))
        except Exception as _:
            return error_response("无此测试数据")
        scene_param_serializer = TestSceneParamsSerializer(instance=scene_param_obj, data=data)
        if scene_param_serializer.is_valid():
            scene_param_serializer.save()
        else:
            return error_response(msg=scene_param_serializer.errors)

        return success_response(msg='success')

    @swagger_auto_schema(
        operation_summary='测试场景-测试用例 数据 删除',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING)],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='删除测试数据'),
            })
    )
    def delete(self, request):
        data = JSONParser().parse(request)
        try:  # 数据如果有误，数据库执行会出错
            with transaction.atomic():
                scene_param_obj = UiSceneParams.objects.get(id=int(data['id']))
                sort = scene_param_obj.sort
                for i in UiSceneParams.objects.filter(sort__gt=sort):
                    i.sort = i.sort - 1
                    i.save()
                scene_param_obj.delete()
                return success_response(msg="删除成功")
        except Exception as _:
            return error_response(msg="删除失败")


class ExecuteScene(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试场景 执行',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_scene_id': openapi.Schema(type=openapi.TYPE_STRING, description='测试场景id'),
                'remote_ip': openapi.Schema(type=openapi.TYPE_STRING, description='执行机ip'),
                'environment_ip': openapi.Schema(type=openapi.TYPE_STRING, description='环境地址'),
                'case_type': openapi.Schema(type=openapi.TYPE_STRING, description='用例类型 /ui'),
            }))
    def post(self, request):
        data = JSONParser().parse(request)
        test_scene_id = int(data.get('test_scene_id'))
        remote_ip = data.get('remote_ip')
        environment_ip = data.get('environment_ip')
        if not test_scene_id or not remote_ip or not environment_ip:
            return error_response("参数传递错误！！！")
        if not UiTestScene.objects.filter(id=int(test_scene_id)):
            return error_response("测试场景不存在！！！")
        case_index_objs = UiSceneTestCaseIndex.objects.filter(scene_id=test_scene_id).order_by("test_case_index")
        if not case_index_objs:
            return error_response('该场景下未关联测试用例')
        try:
            execution_test_case_data = get_one_test_scene_data(test_scene_id, environment_ip, remote_ip)
        except Exception as e:
            return error_response(msg=e.args[0])
        script_execution = ui_script_execution()
        test_report_item = script_execution.execution_ui_scene_case(execution_test_case_data)
        test_report_item['test_type'] = 'UI-场景测试-{}'.format(UiTestScene.objects.get(id=test_scene_id).scene_name)
        test_report_item['tester'] = get_real_name(request)
        ui_report_serializers = UiTestReportSerializers(data=test_report_item)
        if ui_report_serializers.is_valid():
            ui_report_serializers.save()

        return success_response(msg="执行成功")

