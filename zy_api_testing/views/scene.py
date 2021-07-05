from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.views import APIView
from drf_yasg2 import openapi
from django.db.models import Q, Count
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser

from system_settings.tools import success_response, error_response
from zy_api_testing.serializers import SceneSerializerAdd, SceneSerializerQuery
from automated_testing.common.api_response import JsonResponse
from zy_api_testing.models import Scene


class SceneView(APIView):
    authentication_classes = ()
    permission_classes = []


    @swagger_auto_schema(
        operation_summary='业务场景 增加',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'professional_name': openapi.Schema(type=openapi.TYPE_STRING, description='业务名称'),
                'scene_name': openapi.Schema(type=openapi.TYPE_STRING, description='场景名称'),
                'scene_desc': openapi.Schema(type=openapi.TYPE_STRING, description='场景描述'),
                'need_login': openapi.Schema(type=openapi.TYPE_STRING, description='场景是否需要登录'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def post(self, request):
        """项目信息 增加"""
        data = JSONParser().parse(request)
        bs_serializer = SceneSerializerAdd(data=data)
        if bs_serializer.is_valid():
            bs_serializer.save()
            return JsonResponse(data=bs_serializer.data, code="999999", msg="成功")
        else:
            return JsonResponse(msg=bs_serializer.errors, code="999998")

    @swagger_auto_schema(
        operation_summary='业务场景 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的业务ids')
            }))
    def delete(self, request):
        """业务场景 单删群删"""
        data = JSONParser().parse(request)
        delete_ids = data['ids']
        try:
            rows = Scene.objects.filter(pk__in=delete_ids).delete()
        except Exception as e:
            return JsonResponse(code="999998", msg="数据错误!")

        if rows:
            return JsonResponse(code="999999", msg="删除成功!")
        JsonResponse(code="999998", msg="失败!")



    @swagger_auto_schema(
        operation_summary='业务场景 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='professional_name', in_=openapi.IN_QUERY, description='业务名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='scene_name', in_=openapi.IN_QUERY, description='场景名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='scene_desc', in_=openapi.IN_QUERY, description='场景描述', type=openapi.TYPE_STRING),
            openapi.Parameter(name='need_login', in_=openapi.IN_QUERY, description='场景是否需要登录', type=openapi.TYPE_STRING),
        ])


    def get(self, request):
        """业务场景 群查 列表页(多条件筛选)"""
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))

        queryset = Scene.objects.all()
        professional_name = request.GET.get("professional_name")  # 业务名称
        scene_name = request.GET.get("scene_name")  # 场景名称
        scene_desc = request.GET.get("scene_desc")  # 场景描述
        need_login = request.GET.get("need_login")  # 场景描述
        aQ = Q()
        if professional_name:  # 多字段筛选
            aQ.add(Q(professional_name__contains=professional_name), Q.AND)
        if scene_name:
            aQ.add(Q(scene_name__contains=scene_name), Q.AND)
        # if scene_desc:
        #     aQ.add(Q(scene_description__contains=scene_desc), Q.AND)
        # if need_login:
        #     aQ.add(Q(scene_description__contains=need_login), Q.AND)
        queryset = queryset.filter(aQ).order_by("id")
        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)  # 总数量
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)

        serialize = SceneSerializerQuery(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功")



class SceneDetailView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='业务场景查询 单查',
    )
    def get(self, request, pk):
        """业务场景查询 单查"""
        if pk:
            scene_obj = Scene.objects.filter(pk=pk).first()
            if scene_obj:
                bs_serializer = SceneSerializerQuery(scene_obj)
                return JsonResponse(data=bs_serializer.data, code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")

    @swagger_auto_schema(
        operation_summary='业务场景信息 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'professional_name': openapi.Schema(type=openapi.TYPE_STRING, description='业务名称'),
                'scene_name': openapi.Schema(type=openapi.TYPE_STRING, description='场景名称'),
                'scene_desc': openapi.Schema(type=openapi.TYPE_STRING, description='场景描述'),
                'need_login': openapi.Schema(type=openapi.TYPE_STRING, description='场景是否需要登录'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def put(self, request, pk):
        """业务场景 修改 此接口需要先拉取表单数据字典"""
        if pk:
            data = JSONParser().parse(request)
            bs_obj = Scene.objects.filter(id=pk).first()
            if bs_obj:
                server_serializer = SceneSerializerAdd(instance=bs_obj, data=data)
                if server_serializer.is_valid():
                    server_serializer.save()
                else:
                    return JsonResponse(msg=server_serializer.errors, code="999998")
                return JsonResponse(code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")


class SceneSelect(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='业务名称下拉框',
    )
    def get(self, request):
        """业务场景查询 单查"""
        try:
            professional_name_list = [i.get('professional_name') for i in list(Scene.objects.values('professional_name').annotate(c=Count('id')).order_by('professional_name').values('professional_name'))]
            return success_response(data=professional_name_list, msg="成功！！！")
        except Exception as e:
            return error_response("失败！！！")


    @swagger_auto_schema(
        operation_summary='业务树形',
    )
    def post(self, request):
        try:
            professional_name_list = [i.get('professional_name') for i in list(Scene.objects.values('professional_name').annotate(c=Count('id')).order_by('professional_name').values('professional_name'))]
            end_list = []
            for professional_name in professional_name_list:
                item = {}
                item['scene_name'] = professional_name
                scene_objs = Scene.objects.filter(professional_name=professional_name)
                children_list = []
                for scene_obj in scene_objs:
                    children_data = {}
                    children_data['id'] = scene_obj.id
                    children_data['scene_name'] = scene_obj.scene_name
                    children_list.append(children_data)
                item['children'] = children_list
                end_list.append(item)
            return success_response(data=end_list, msg='成功！！！')
        except Exception as e:
            return error_response(str(e))
            # return error_response("失败！！！")



