from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from drf_yasg2 import openapi
from django.contrib import auth
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView
from account_system.models import UserProfile, PermissionViewResources
from account_system.serializers import UserSerializerAdd, UserSerializerQuery, PermissionResourcesSerializerQuery
from automated_testing.common.api_response import JsonResponse
from rest_framework.permissions import AllowAny
from django.db import transaction
from rest_framework.parsers import JSONParser
from django.db.models import Q
import base64


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = (AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    @swagger_auto_schema(
        operation_summary='用户登录体系-登录(创建token)',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='用户名称'),

                'password': openapi.Schema(type=openapi.TYPE_STRING, description='登录密码'),
            }))
    def post(self, request, *args, **kwargs):
        """
        用户登录
        """
        errorInfo = u''
        data = request.data
        username = data.get('username')
        password = data.get('password')
        try:
            user = auth.authenticate(username=username, password=password)
            visit_count = user.Numberofvisits
        except Exception as e:
            return JsonResponse(code='999998', msg="用户名或密码错误")
        try:
            tokenObj = Token.objects.get(user_id=user.id)
        except Exception as e:
            tokenObj = Token.objects.create(user=user)
        # tokenObj = Token.objects.create(user=user)
        # 获取token字符串
        user.Numberofvisits = visit_count + 1
        user.save()
        token = tokenObj.key
        return JsonResponse(code='999999', data={'HTTP_AUTHORIZATION': token}, msg=errorInfo)



class UserView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='用户信息 列表页 多条件筛选',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='page_size',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='page',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='Real_name', in_=openapi.IN_QUERY, description='Real_name',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='username', in_=openapi.IN_QUERY, description='username', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 10))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code="999985", msg="page_size/page参数必须为int")
        aQ = Q()
        Real_name = request.GET.get('Real_name')
        username = request.GET.get('username')
        queryset = UserProfile.objects.all()
        if Real_name:
            aQ.add(Q(Real_name__contains=Real_name), Q.AND)
        if username:
            aQ.add(Q(username__contains=username), Q.AND)
        queryset = queryset.filter(aQ).order_by("id")
        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)
        try:
            obm = paginator.page(page)
        except PageNotAnInteger:
            obm = paginator.page(1)
        except EmptyPage:
            obm = paginator.page(paginator.num_pages)

        serialize = UserSerializerQuery(obm, many=True)
        return JsonResponse(data={"data": serialize.data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功")

    @swagger_auto_schema(
        operation_summary='用户新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'department': openapi.Schema(type=openapi.TYPE_INTEGER, description='所属部门id', default=1),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='用户名'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码 base64加密'),
                'Repeat_password': openapi.Schema(type=openapi.TYPE_STRING, description='请重复密码 base64加密'),
                'Real_name': openapi.Schema(type=openapi.TYPE_STRING, description='真实姓名'),
                'gender': openapi.Schema(type=openapi.TYPE_INTEGER, description='性别id 1/0 男/女'),
                'Entry_date': openapi.Schema(type=openapi.TYPE_STRING, description='入职日期'),
                'position': openapi.Schema(type=openapi.TYPE_INTEGER, description='职位id', default=1),
                'permission_group': openapi.Schema(type=openapi.TYPE_INTEGER, description='权限分组id', default=1),
                'mailbox': openapi.Schema(type=openapi.TYPE_STRING, description='邮箱'),
                'Telephone': openapi.Schema(type=openapi.TYPE_STRING, description='联系方式'),
                'QQ': openapi.Schema(type=openapi.TYPE_STRING, description='QQ'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }))
    def post(self, request):
        data = JSONParser().parse(request)
        if 'Repeat_password' not in data or 'password' not in data:
            return JsonResponse(code="999998", msg="密码为必填字段")
        else:
            Repeat_password = base64.b64decode(data["Repeat_password"]).decode("utf-8")
            password = base64.b64decode(data["password"]).decode("utf-8")
            if password != Repeat_password:
                return JsonResponse(code="999998", msg="密码不一致")
        username = data['username']
        user = UserProfile.objects.filter(username=username)
        if user:
            return JsonResponse(code="999998", msg="用户已经存在")
        data['password'] = make_password(password)
        if request.user.is_authenticated:
            data['creator'] = request.user.username
        else:
            data['creator'] = "admin"
        ser = UserSerializerAdd(data=data)
        if ser.is_valid():
            ser.save()
            return JsonResponse(code="999999", msg="成功", data=ser.data.get('id'))
        else:
            return JsonResponse(msg=ser.errors, code="999998")

    @swagger_auto_schema(
        operation_summary='删除用户',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='删除用户的id列表')
            }))
    def delete(self, request):
        """服务器 单删群删"""
        data = JSONParser().parse(request)
        delete_ids = data['ids']
        try:  # 数据如果有误，数据库执行会出错
            rows = UserProfile.objects.filter(pk__in=delete_ids).delete()
        except Exception as e:
            return JsonResponse(code="999998", msg="数据错误!")

        if rows:
            return JsonResponse(code="999999", msg="删除成功!")
        JsonResponse(code="999998", msg="失败!")


class UserDetailView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='用户信息 单查',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"),
        ],

    )
    def get(self, request, pk):
        if pk:
            user_obj = UserProfile.objects.filter(pk=pk).first()
            if user_obj:
                user_serializer = UserSerializerQuery(user_obj)
                return JsonResponse(data=user_serializer.data, code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")

    @swagger_auto_schema(
        operation_summary='用户信息 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'department': openapi.Schema(type=openapi.TYPE_INTEGER, description='所属部门id', default=1),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='用户名'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码 base64加密'),
                'Repeat_password': openapi.Schema(type=openapi.TYPE_STRING, description='请重复密码 base64加密'),
                'Real_name': openapi.Schema(type=openapi.TYPE_STRING, description='真实姓名'),
                'gender': openapi.Schema(type=openapi.TYPE_INTEGER, description='性别id 1/0 男/女'),
                'Entry_date': openapi.Schema(type=openapi.TYPE_STRING, description='入职日期'),
                'position': openapi.Schema(type=openapi.TYPE_INTEGER, description='职位id', default=1),
                'permission_group': openapi.Schema(type=openapi.TYPE_INTEGER, description='权限分组id', default=1),
                'mailbox': openapi.Schema(type=openapi.TYPE_STRING, description='邮箱'),
                'Telephone': openapi.Schema(type=openapi.TYPE_STRING, description='联系方式'),
                'QQ': openapi.Schema(type=openapi.TYPE_STRING, description='QQ'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }))
    def put(self, request, pk):
        data = JSONParser().parse(request)
        if 'Repeat_password' and 'password' in data:
            Repeat_password = base64.b64decode(data["Repeat_password"]).decode("utf-8")
            password = base64.b64decode(data["password"]).decode("utf-8")
            if password != Repeat_password:
                return JsonResponse(data={}, code="999998", msg="密码不一致")
            data['password'] = make_password(password)
        try:
            user = UserProfile.objects.get(id=int(pk))
        except Exception as e:
            return JsonResponse(data={}, code="999998", msg="用户不存在")
        ser = UserSerializerAdd(user, data=data)  # UserSerializer用户新增修改serializer

        with transaction.atomic():
            if ser.is_valid():
                ser.save()
                return JsonResponse(code="999999", msg="成功")
            else:
                return JsonResponse(msg=ser.errors, code="999998")


class LogoutView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='用户登录体系-登出(删除token)',
        manual_parameters=[
            openapi.Parameter(name='Authorization', in_=openapi.IN_HEADER, description='Authorization', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            tokenObj = Token.objects.get(key=token.replace("token ", ""))
            tokenObj.delete()
            return JsonResponse(msg='注销成功', code="999999")
        except Exception as _:
            return JsonResponse(msg='请重新登陆', code="999999")


class UserInfoView(APIView):
    permission_classes = ()
    serializer_class = AuthTokenSerializer

    @swagger_auto_schema(
        operation_summary='当前用户信息 查询',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, )
        ]
    )
    def post(self, request):
        """获取用户信息接口"""
        # username = request.user.username
        #
        # data = {"name": "ADMINUSER", "avatar": "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
        #         "permission": "no", 'roles': ['admmin', 'editor'], 'introduction': 'this is Noe'}
        # return JsonResponse(data=data, code="999999", msg="成功")
        token = request.META.get('HTTP_AUTHORIZATION')
        token_obj = Token.objects.get(key=token)
        user_obj = token_obj.user
        user_serializer = UserSerializerQuery(user_obj)
        return_data = user_serializer.data
        return_data['avatar'] = ''
        return JsonResponse(data=return_data, code="999999", msg="成功")


class PermissionInfoView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def get_permission_resource_tree(self, root_permission_resource_dict, all_permission_resource_dict):
        permission_resource_id = root_permission_resource_dict['id']
        # if permission_resource_id == 6:
        #     print(111)
        permission_resource_dicts = [i for i in all_permission_resource_dict.values() if i['super_resource_id'] == str(permission_resource_id)]
        for permission_resource_dict in permission_resource_dicts:
            if self.is_superuser:
                permission_resource_dict['is_allow'] = True
            else:
                permission_resource_dict['is_allow'] = True if str(permission_resource_dict['id']) in self.permission_ids else False
            permission_resource_dict['children'] = []

            self.get_permission_resource_tree(permission_resource_dict, all_permission_resource_dict)
            root_permission_resource_dict['children'].append(permission_resource_dict)

    @swagger_auto_schema(
        operation_summary='当前用户权限 查询',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, )
        ]
    )
    def post(self, request, *args, **kwargs):
        """获取权限信息接口"""
        token = request.META.get('HTTP_AUTHORIZATION')
        token_obj = Token.objects.get(key=token)
        user_obj = token_obj.user
        self.is_superuser = False
        if user_obj.is_superuser == 1:
            self.is_superuser = True
        permission_resource_serializer = PermissionResourcesSerializerQuery(user_obj)
        return_data = permission_resource_serializer.data

        if user_obj.permission_group:
            permission_ids = user_obj.permission_group.permission_ids
            if permission_ids:
                if '_' in permission_ids:
                    self.permission_ids = permission_ids.split('_')
                else:
                    self.permission_ids = [permission_ids]
            else:
                self.permission_ids = []
        else:
            self.permission_ids = []
        tree_data = []

        root_permission_resource_objs = PermissionViewResources.objects.all()
        root_permission_resource_dicts = PermissionResourcesSerializerQuery(root_permission_resource_objs, many=True)
        all_permission_resource_dict = {i['id']: i for i in root_permission_resource_dicts.data}
        root_permission_resource_dict = {i['id']: i for i in root_permission_resource_dicts.data if not i['super_resource_id']}
        for root_permission_resource_dict in root_permission_resource_dict.values():
            root_permission_resource_dict['children'] = []
            self.get_permission_resource_tree(root_permission_resource_dict, all_permission_resource_dict)
            tree_data.append(root_permission_resource_dict)
        return_data['permission'] = tree_data
        return JsonResponse(data=return_data, code="999999", msg="成功")

