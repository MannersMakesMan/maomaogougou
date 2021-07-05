from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from system_settings.tools import success_response, error_response
from system_settings.models import Dataexplain, DataDictionary
from system_settings.serializers import *

from zy_api_testing.tools import api_list_query

BASE_CODE_LIST = ['A0000001', 'A0000002']


def get_new_code():
    # 返回父字典递增的新 编码
    code_list = list(Dataexplain.objects.all().values('dictionary_code'))
    int_code_list = []
    for code in code_list:
        try:
            int_code = int(code.get('dictionary_code')[1:])
            int_code_list.append(int_code)
        except:
            pass
    if len(int_code_list)>0:
        new_value = str(max(int_code_list)+1)
        new_code = 'A' + '0'*(7-len(new_value))+new_value
    else:
        new_code = 'A0000001'
    return new_code


def get_new_son_dict_code(Dataexplain_id):
    # 返回父字典递增的新 编码
    code_list = list(DataDictionary.objects.filter(Dataexplain_id=Dataexplain_id).values('DictionarySubitem_code'))
    int_code_list = []
    for code in code_list:
        try:
            int_code = int(code.get('DictionarySubitem_code')[1:])
            int_code_list.append(int_code)
        except:
            pass
    if len(int_code_list) > 0:
        new_value = str(max(int_code_list)+1)
        new_code = 'a' + '0'*(7-len(new_value))+new_value
    else:
        new_code = 'a0000001'
    return new_code


class DataDictList(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='数据字典页面 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='dictionary_code', in_=openapi.IN_QUERY, description='字典编码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='dictionary_explain', in_=openapi.IN_QUERY, description='字典描述', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            total, obm = api_list_query(data, page, page_size, Dataexplain, 'id', ['dictionary_code', 'dictionary_explain'])
            try:
                data_dict_serialize = DataDictionarySerializerQuery(obm, many=True)
                return_data = data_dict_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='数据字典 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的数据字典 id列表 '),
            }))
    def delete(self, request):
        """数据字典 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data.get('ids')
                for id in delete_ids:
                    if id in BASE_CODE_LIST:
                        raise Exception('IS_BASE')
                    data_dict_obj = Dataexplain.objects.filter(id=id)
                    if data_dict_obj:
                        # 校验改字典项下是否子项
                        son_dict = DataDictionary.objects.filter(Dataexplain_id=data_dict_obj.first().id)
                        if son_dict:
                            return error_response(msg="改字典下存在子项数据 ， 无法删除！！")
                        data_dict_obj.first().delete()
                    else:
                        return error_response(msg="数据错误!")
                return success_response(data='', msg="成功!")
        except Exception as e:
            if str(e) == 'IS_BASE':
                return error_response('基础配置字典无法删除！！！')
            return error_response(msg='删除失败！')


    @swagger_auto_schema(
        operation_summary='数据字典 新增',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'dictionary_explain': openapi.Schema(type=openapi.TYPE_STRING, description='数据字典描述'),
            }
        )
    )
    def post(self, request):
        """数据字典 增加"""
        try:
            data = JSONParser().parse(request)
            data['dictionary_code'] = get_new_code()
            data_dict_serializer = DataDictionarySerializerAdd(data=data)
            if data_dict_serializer.is_valid():
                return_data = data_dict_serializer.save()
                return success_response(data=model_to_dict(return_data), msg='数据字典信息新增成功！')
            else:
                return error_response(msg=data_dict_serializer.errors)
        except Exception as e:
            return error_response(msg='失败!!')

    @swagger_auto_schema(
        operation_summary='场景配置api 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='字典id'),
                'dictionary_explain': openapi.Schema(type=openapi.TYPE_STRING, description='数据字典描述'),
            }
        )
    )
    def put(self, request):
        try:
            data = JSONParser().parse(request)
            pk = data.get('id')
            if not pk:
                return error_response(msg='id 为空')
            data_dict_obj = Dataexplain.objects.filter(id=pk)
            if not data_dict_obj:
                return error_response(msg='id错误！！')
            data['dictionary_code'] = data_dict_obj.first().dictionary_code
            data_dict_serializer = DataDictionarySerializerAdd(instance=data_dict_obj.first(), data=data)
            if data_dict_serializer.is_valid():
                return_data = data_dict_serializer.save()
                return success_response(data=model_to_dict(return_data), msg="修改成功!!!")
            else:
                return error_response(msg=data_dict_serializer.errors)
        except Exception as e:
            return error_response(msg='失败!!')


class SonDataDict(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='子数据字典页面 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='Dataexplain_id', in_=openapi.IN_QUERY, description='父字典id', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            if not data.get('Dataexplain_id'):
                return error_response('未传递父级字典id!')
            data_dict_obj = Dataexplain.objects.filter(id=data.get('Dataexplain_id'))
            if not data_dict_obj:
                return error_response('无效父级id!')
            total, obm = api_list_query(data, page, page_size, DataDictionary, 'id', ['Dataexplain_id'], has_parent=True)
            try:
                data_dict_serialize = SonDataDictionarySerializerQuery(obm, many=True)
                return_data = data_dict_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='子数据字典 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的子数据字典 id列表 '),
            }))
    def delete(self, request):
        """数据字典 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data.get('ids')
                for id in delete_ids:
                    data_dict_obj = DataDictionary.objects.filter(id=id)
                    if data_dict_obj:
                        print(data_dict_obj.first().Dataexplain_id)
                        if data_dict_obj.first().Dataexplain_id.dictionary_code in BASE_CODE_LIST:
                            raise Exception('IS_BASE')
                        data_dict_obj.first().delete()
                    else:
                        return error_response(msg="数据错误!")
                return success_response(data='', msg="成功!")
        except Exception as e:
            if str(e) == 'IS_BASE':
                return error_response(msg='基础字典数据无法删除！')
            return error_response(msg='删除失败！')


    @swagger_auto_schema(
        operation_summary='子数据字典 新增',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Dataexplain_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='父数据字典id'),
                'DictionarySubitem_explain': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典描述'),
                'dictionary_item1': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典参数1'),
                'dictionary_item2': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典参数2'),
                'dictionary_item3': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典参数3'),
                'item_desc': openapi.Schema(type=openapi.TYPE_STRING, description='字典子项参数说明'),
    }
        )
    )
    def post(self, request):
        """数据字典 增加"""
        try:
            data = JSONParser().parse(request)
            data['DictionarySubitem_code'] = get_new_son_dict_code(data.get('Dataexplain_id'))
            data_dict_serializer = SonDataDictionarySerializerAdd(data=data)
            if data_dict_serializer.is_valid():
                return_data = data_dict_serializer.save()
                return success_response(data=model_to_dict(return_data), msg='数据字典子项信息新增成功！')
            else:
                return error_response(msg=data_dict_serializer.errors)
        except Exception as e:
            return error_response(msg='失败!!')

    @swagger_auto_schema(
        operation_summary='场景配置api 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='子数据字典id'),
                'DictionarySubitem_explain': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典描述'),
                'dictionary_item1': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典参数1'),
                'dictionary_item2': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典参数2'),
                'dictionary_item3': openapi.Schema(type=openapi.TYPE_STRING, description='子数据字典参数3'),
                'item_desc': openapi.Schema(type=openapi.TYPE_STRING, description='字典子项参数说明'),
            }
        )
    )
    def put(self, request):
        try:
            data = JSONParser().parse(request)
            pk = data.get('id')
            if not pk:
                return error_response(msg='id 为空')
            data_dict_obj = DataDictionary.objects.filter(id=pk)
            if not data_dict_obj:
                return error_response(msg='id错误！！')
            data['Dataexplain_id'] = data_dict_obj.first().Dataexplain_id.id
            data['DictionarySubitem_code'] = data_dict_obj.first().DictionarySubitem_code
            data_dict_serializer = SonDataDictionarySerializerAdd(instance=data_dict_obj.first(), data=data)
            if data_dict_serializer.is_valid():
                return_data = data_dict_serializer.save()
                return success_response(data=model_to_dict(return_data), msg="修改成功!!!")
            else:
                return error_response(msg=data_dict_serializer.errors)
        except Exception as e:
            return error_response(msg='失败!!')
