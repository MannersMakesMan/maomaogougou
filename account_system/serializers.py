import datetime

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from account_system.models import UserProfile, Department, Position, PermissionGroup, PermissionViewResources
import hashlib


class TokenSerializer(serializers.ModelSerializer):
    """
    """
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    # phone = serializers.CharField(source="user.user.phone")
    email = serializers.CharField(source="user.email")
    date_joined = serializers.CharField(source="user.date_joined")

    class Meta:
        model = Token
        fields = ('first_name', 'last_name', 'email', 'key', 'date_joined')


class UserSerializerAdd(serializers.ModelSerializer):
    # 用户信息新增与修改字段规则校验
    department = serializers.CharField(required=False, error_messages={
                                         'required': '所属部门为必填信息',
                                     })
    username = serializers.CharField(required=True, min_length=4, max_length=20,
                                     error_messages={
                                         'required': '用户名字段为必填信息',
                                         'min_length': '用户名请输入4~20个字符',
                                         'max_length': '用户名请输入4~20个字符'
                                     })
    password = serializers.CharField(required=False, min_length=6, max_length=128,
                                     error_messages={
                                         'min_length': '用户密码为6~80个字符',
                                         'max_length': '用户密码为6~80个字符'
                                     })
    Real_name = serializers.CharField(required=True, min_length=2, max_length=30,
                                      error_messages={
                                          'required': '真实用户名字段为必填信息',
                                          'min_length': '真实用户名请输入6~30个字符',
                                          'max_length': '真实用户名请输入6~30个字符'
                                      })
    Entry_date = serializers.CharField(required=False)
    position = serializers.CharField(required=False, error_messages={'required': '请正确选择职位信息'})
    permission_group = serializers.CharField(required=False, error_messages={'required': '请正确选择权限分组信息'})

    mailbox = serializers.EmailField(required=False, allow_null=True, allow_blank=True,
                                     error_messages={'required': '请正确输入邮箱信息'})
    gender = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                   error_messages={'required': '请正确选择性别信息'})
    Telephone = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                      error_messages={'required': '手机号码为11位数字请确认输入是否正确！'})
    QQ = serializers.CharField(required=False, allow_null=True, allow_blank=True, min_length=5, max_length=15,
                               error_messages={
                                   'min_value': 'QQ请输入5~15个字符',
                                   'max_value': 'QQ请输入5~15个字符'
                               })
    remark = serializers.CharField(required=False, allow_null=True, allow_blank=True, min_length=0, max_length=300,
                                   error_messages={
                                       'max_length': '备注不超过300个字符'
                                   })
    def validate_Entry_date(self, Entry_date):
        try:
            date = datetime.datetime.strptime(Entry_date, '%Y-%m-%d').date()
            return date
        except:
            raise serializers.ValidationError('日期格式错误')

    def validate_department(self, department):
        try:
            department_obj = Department.objects.get(id=department)
            return department_obj
        except:
            raise serializers.ValidationError('改部门不存在')

    def validate_permission_group(self, permission_group):
        try:
            permission_group_obj = PermissionGroup.objects.get(id=permission_group)
            return permission_group_obj
        except:
            raise serializers.ValidationError('权限组不存在')

    def validate_position(self, position):
        try:
            position_obj = Position.objects.get(id=position)
            return position_obj
        except:
            raise serializers.ValidationError('权限组不存在')

    class Meta:
        model = UserProfile
        fields = ('id', 'department', 'username', 'password', 'Real_name', "Entry_date", "position",
                  "permission_group", "mailbox", 'gender', 'Telephone', 'QQ', 'remark', 'gender')


class UserSerializerQuery(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    username = serializers.CharField()
    password = serializers.SerializerMethodField()
    Real_name = serializers.CharField()
    Entry_date = serializers.DateField()
    position = serializers.SerializerMethodField()
    permission_group = serializers.SerializerMethodField()
    mailbox = serializers.CharField()
    gender = serializers.SerializerMethodField()
    Telephone = serializers.CharField()
    QQ = serializers.CharField()
    remark = serializers.CharField()
    update_time = serializers.DateTimeField()

    def get_department(self, obj):
        if obj.department:
            return obj.department.department_name
        else:
            return None

    def get_password(self, obj):
        return None

    def get_position(self, obj):
        if obj.position:
            return obj.position.position_name
        else:
            return None

    def get_permission_group(self, obj):
        if obj.permission_group:
            return obj.permission_group.permission_group_name
        else:
            return None

    def get_gender(self, obj):
        if obj.gender:
            if obj.gender in ["0", "1"]:
                return obj.get_gender_display()
        else:
            return None

    class Meta:
        model = UserProfile
        fields = ('id', 'department', 'username', 'password', 'Real_name', "Entry_date", "position",
                  "permission_group", "mailbox", 'gender', 'Telephone', 'QQ', 'remark', 'update_time')


class DepartmentSerializerAdd(serializers.ModelSerializer):
    # 部门信息新增与修改字段规则校验
    department_name = serializers.CharField(required=True, min_length=1, max_length=64,
                                            error_messages={
                                                'required': '部门名称为必填字段信息',
                                                'min_length': '部门名称字段长度为1~64位字符',
                                                'max_length': '部门名称字段长度为1~64位字符'
                                            })
    department_code = serializers.CharField(required=True, min_length=1, max_length=64,
                                            error_messages={
                                                'required': '部门代码为必需字段信息',
                                                'min_length': '部门代码字段长度为1~64位字符',
                                                'max_length': '部门代码字段长度为1~64位字符'
                                            })
    remark = serializers.CharField(required=False, min_length=1, max_length=64,
                                   error_messages={
                                       'min_length': '备注长度为1~64位字符',
                                       'max_length': '备注字段长度为1~64位字符'
                                   })

    def validate_department_name(self, department_name):
        if Department.objects.filter(department_name=department_name) and not self.initial_data.get('id'):
            raise serializers.ValidationError("该部门信息已存在")
        elif Department.objects.filter(department_name=department_name).exclude(id=self.initial_data.get('id')):
            raise serializers.ValidationError("该部门名称已存在")
        return department_name

    def validate_super_department_id(self, super_department_id):
        if super_department_id:
            if not Department.objects.filter(id=super_department_id):
                raise serializers.ValidationError("该上级部门信息不存在")
        return super_department_id

    class Meta:
        model = Department
        fields = ('id', 'department_name', 'department_code', 'super_department_id', 'super_department_name', 'super_department_code', 'remark')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'department_code', 'department_name', 'superdepartment', 'level','remark')


class DepartmentSerializerQuery(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'department_code', 'department_name', 'super_department_id', 'super_department_name', 'remark', 'super_department_code')


class PositionSerializerQuery(serializers.ModelSerializer):
    # 职位查询
    class Meta:
        model = Position
        fields = ("id", "position_name", "position_desc", "create_time", "update_time", "remark")


class PositionLsSerializerQuery(serializers.ModelSerializer):
    # 职位列表 下拉框
    class Meta:
        model = Position
        fields = ("id", "position_name")


class PositionSerializerAdd(serializers.ModelSerializer):
    # 职位添加
    position_name = serializers.CharField(required=True, min_length=0, max_length=10,
                                         error_messages={'max_length': '职位名称 不能大于10个字符',
                                                         'required': '权限分组名称为必填字段信息'})
    position_desc = serializers.CharField(required=False, min_length=0, max_length=30,
                                         error_messages={'max_length': '职位描述 不能大于30个字符'})
    remark = serializers.CharField(required=False, min_length=0, max_length=30,
                                         error_messages={'max_length': '备注 不能大于30个字符'})

    class Meta:
        model = Position
        fields = ("position_name", "position_desc", "remark")


class PermissionGroupSerializerQuery(serializers.ModelSerializer):
    # 权限组 查询
    user_ls = serializers.SerializerMethodField()
    permission_group_name = serializers.CharField()
    permission_group_desc = serializers.CharField()

    def get_user_ls(self, obj):
        user_ls = [i.Real_name for i in obj.user_PermissionGroup.all()]
        return user_ls

    class Meta:
        model = PermissionGroup
        fields = ("id", "permission_group_name", "permission_group_desc", "user_ls")


class PermissionGroupLsSerializer(serializers.ModelSerializer):
    # 权限组 列表 下拉框
    class Meta:
        model = PermissionGroup
        fields = ("id", "permission_group_name")


class PermissionGroupSerializerAdd(serializers.ModelSerializer):
    # 权限组 增加
    permission_group_name = serializers.CharField(required=True, min_length=1, max_length=64,
                                             error_messages={
                                                 'required': '权限分组名称为必填字段信息',
                                                 'min_length': '权限分组名称长度为1~64位字符',
                                                 'max_length': '权限分组名称长度为1~64位字符'
                                             })
    permission_group_desc = serializers.CharField(required=False, min_length=0, max_length=64,
                                             error_messages={
                                                 'min_length': '权限分组描述长度为1~64位字符',
                                                 'max_length': '权限分组描述长度为1~64位字符'
                                             })

    class Meta:
        model = PermissionGroup
        fields = ("id", "permission_group_name", "permission_group_desc")


class PermissionResourcesSerializerQuery(serializers.ModelSerializer):
    # 权限资源 查询
    class Meta:
        model = PermissionViewResources
        fields = ("id", "name", "path_eng", "assembly_name", "page_identification", "super_resource_id", "redirect")
