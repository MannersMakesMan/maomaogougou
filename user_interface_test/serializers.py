import json
import re
import time

from rest_framework import serializers

from account_system.models import UserProfile
from account_system.serializers import UserSerializerQuery
from system_settings.models import Project
from system_settings.serializers import ProjectSerializerQuery
from user_interface_test.models import CommonParams, TestAppModel, TestCase, TestCaseData, UiTestScene, UiSceneParams
from user_interface_test.models import CommonParams, UiFunctions


class UiTestParamsSerializerQuery(serializers.ModelSerializer):
    entry_name_id = serializers.SerializerMethodField()

    def get_entry_name_id(self, obj):
        if obj.entry_name_id:
            data = ProjectSerializerQuery(Project.objects.filter(id=obj.entry_name_id).first()).data
            return {
                'id': data.get('id'),
                'entry_name': data.get('entry_name'),
                'project_manager': data.get('project_manager'),
                'Test_Leader': data.get('Test_Leader'),
            }
        else:
            return None

    class Meta:
        model = CommonParams
        fields = ('id', 'entry_name_id', 'param_desc', 'param_value', 'update_user', 'create_time', 'update_time', 'remark')


class UiTestParamsDropDownBoxSerializerQuery(serializers.ModelSerializer):
    class Meta:
        model = CommonParams
        fields = ('param_desc', 'param_value')


class UiTestParamsSerializerAdd(serializers.ModelSerializer):
    entry_name_id = serializers.IntegerField()
    param_desc = serializers.CharField(required=True, error_messages={'required': '参数名不能为空'})
    param_value = serializers.CharField(required=True, error_messages={'required': '参数值'})
    # remark = serializers.CharField(required=False)

    def validate_entry_name_id(self, entry_name_id):
        if not Project.objects.filter(id=entry_name_id):
            raise serializers.ValidationError('项目错误！！！')
        return entry_name_id

    class Meta:
        model = CommonParams
        fields = ('id', 'entry_name_id', 'param_desc', 'param_value', 'update_user', 'remark')


class UiFunctionsSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = UiFunctions
        fields = ('function', 'is_need_value', 'is_need_button', 'function_level', 'super_function', 'description')

class UiFunctionsSerializerQuery(serializers.ModelSerializer):
    class Meta:
        model = UiFunctions
        fields = ('id', 'function', 'is_need_value', 'is_need_button', 'function_level', 'super_function', 'description')


class TestModelSerializerQuery(serializers.ModelSerializer):
    model_name = serializers.CharField()
    dev_user = serializers.SerializerMethodField()
    test_user = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField()
    update_time = serializers.DateTimeField()
    remark = serializers.CharField()
    update_user = serializers.CharField()

    def get_dev_user(self, obj):
        if obj.dev_user:
            data = UserSerializerQuery(UserProfile.objects.filter(id=obj.dev_user).first()).data
            return {
                'id': data.get('id'),
                'Real_name': data.get('Real_name')
            }
        else:
            return None

    def get_test_user(self, obj):
        if obj.test_user:
            data = UserSerializerQuery(UserProfile.objects.filter(id=obj.test_user).first()).data
            return {
                'id': data.get('id'),
                'Real_name': data.get('Real_name')
            }
        else:
            return None

    class Meta:
        model = TestAppModel
        fields = ('id', 'model_name', 'model_level', 'dev_user', 'test_user', 'remark', 'update_user', 'create_time', 'update_time')


class TestModelSerializerAdd(serializers.ModelSerializer):
    model_level = serializers.IntegerField()
    # super_id = serializers.IntegerField()
    model_name = serializers.CharField(required=True, error_messages={'required': '模块名为空'})
    dev_user = serializers.CharField()
    test_user = serializers.CharField()

    def validate_entry_name_id(self, entry_name_id):
        if self.initial_data['model_level'] == 1:
            if not Project.objects.filter(id=entry_name_id):
                raise serializers.ValidationError('没有此项目！！！')
        else:
            if not TestAppModel.objects.get(model_level=1, id=self.initial_data['super_id']):
                raise serializers.ValidationError('没有此模块！！！')
        return entry_name_id

    def validate_dev_user(self, dev_user):
        if not UserProfile.objects.filter(id=dev_user):
            raise serializers.ValidationError('开发负责人id错误！！！')
        return dev_user

    def validate_test_user(self, test_user):
        if not UserProfile.objects.filter(id=test_user):
            raise serializers.ValidationError('测试负责人id错误！！！')
        return test_user

    class Meta:
        model = TestAppModel
        fields = ('id', 'model_name', 'model_level', 'dev_user', 'test_user', 'remark', 'update_user', 'super_id')


class TestModelSelectSerializerQuery(serializers.ModelSerializer):
    model_name = serializers.CharField()

    class Meta:
        model = TestAppModel
        fields = ('id', 'model_name')


class TestCaseQuerySerializers(serializers.ModelSerializer):
    test_app_model_id = serializers.SerializerMethodField()
    case_number = serializers.CharField()
    case_name = serializers.CharField()
    case_type = serializers.CharField()
    failed_up = serializers.CharField()
    update_user = serializers.CharField()
    is_common_function = serializers.IntegerField()
    create_time = serializers.DateTimeField()
    update_time = serializers.DateTimeField()
    remark = serializers.CharField()

    def get_test_app_model_id(self, obj):
        if obj.test_app_model_id:
            model_obj = TestAppModel.objects.filter(id=obj.test_app_model_id).first()
            return {
                'id': model_obj.id,
                'model_name': model_obj.model_name,
            }
        else:
            return None

    class Meta:
        model = TestCase

        fields = ('id', 'test_app_model_id', 'case_number', 'case_name', 'case_type', 'failed_up', 'update_user', 'create_time', 'update_time', 'remark', 'is_common_function')


class TestCaseAddSerializer(serializers.ModelSerializer):
    test_app_model_id = serializers.CharField()
    case_number = serializers.CharField()
    case_name = serializers.CharField()
    case_type = serializers.CharField()
    failed_up = serializers.CharField()
    update_user = serializers.CharField()
    is_common_function = serializers.IntegerField(required=True, min_value=0, max_value=1, error_messages={'required': '是否是公共方法 不能为空',
                                                                                                         'min_value': '操作系统 请输入0-1之间的值',
                                                                                                         'max_value': '操作系统 请输入0-1之间的值'})


    def validate_test_app_model_id(self, test_app_model_id):
        if not TestAppModel.objects.filter(id=test_app_model_id):
            raise serializers.ValidationError('界面不存在')
        return test_app_model_id

    class Meta:
        model = TestCase

        fields = ('id', 'test_app_model_id', 'case_number', 'case_name', 'case_type', 'failed_up', 'update_user', 'remark', 'is_common_function')


class TestCaseDataSerializerQuery(serializers.ModelSerializer):
    test_case_id = serializers.CharField()
    step_desc = serializers.CharField()
    field_desc = serializers.SerializerMethodField()
    location_func = serializers.CharField()
    operate_func = serializers.CharField()
    action_func = serializers.CharField()
    location_value = serializers.CharField()
    func_param = serializers.SerializerMethodField()
    ele_attribute = serializers.CharField()
    assert_value = serializers.CharField()
    update_user = serializers.CharField()
    create_time = serializers.DateTimeField()
    update_time = serializers.DateTimeField()
    extension = serializers.CharField()
    sort = serializers.IntegerField()
    func_common_param_id = serializers.IntegerField()
    is_need_button = serializers.IntegerField()
    is_need_value = serializers.IntegerField()
    is_need_assert = serializers.IntegerField()

    def get_func_param(self, obj):
        # 若具有公共参数 则返回公共参数值 作为回显
        if obj.func_common_param_id:
            param_objs = CommonParams.objects.filter(id=obj.func_common_param_id)
            if param_objs:
                param_value = param_objs[0].param_value
                return param_value
            else:
                return obj.func_param
        else:
            return obj.func_param

    def get_field_desc(self, obj):
        if obj.func_common_param_id:
            param_objs = CommonParams.objects.filter(id=obj.func_common_param_id)
            if param_objs:
                field_desc = param_objs[0].param_desc
                return field_desc
            else:
                return obj.field_desc
        else:
            return obj.field_desc


    class Meta:
        model = TestCaseData
        fields = '__all__'


class TestCaseDataSerializerAdd(serializers.ModelSerializer):
    test_case_id = serializers.CharField()
    step_desc = serializers.CharField(required=True, error_messages={'required': '测试步骤描述为空'})
    action_func = serializers.CharField(required=False)
    sort = serializers.IntegerField(required=True, error_messages={'required': '排序值为空'})

    def validate_test_case_id(self, test_case_id):
        if not TestCase.objects.filter(id=test_case_id):
            raise serializers.ValidationError('测试用例不存在')
        return test_case_id

    def validate_action_func(self, action_func):
        return eval(action_func)

    class Meta:
        model = TestCaseData
        fields = ('test_case_id', 'step_desc', 'field_desc', 'location_func', 'operate_func', 'action_func', 'location_value', 'func_param', 'extension', 'sort', 'update_user', 'func_common_param_id', 'is_need_value', 'is_need_button', 'is_need_assert', 'func_common_param_id', 'ele_attribute', 'assert_value', "mysql_info_id", "is_need_mysql")


class TestSceneSerializerQuery(serializers.ModelSerializer):
    model_name = serializers.CharField()
    fun_name = serializers.CharField()
    scene_name = serializers.CharField()
    scene_desc = serializers.CharField()
    update_user = serializers.CharField()
    create_time = serializers.DateTimeField()
    update_time = serializers.DateTimeField()
    reMark = serializers.CharField()

    class Meta:
        model = UiTestScene
        fields = '__all__'


class TestSceneSerializerAdd(serializers.ModelSerializer):
    model_name = serializers.CharField(required=True, error_messages={'required': '模块名称为空'})
    fun_name = serializers.CharField(required=True, error_messages={'required': '功能名称为空'})
    scene_name = serializers.CharField(required=True, error_messages={'required': '执行场景id列表为空'})
    scene_desc = serializers.CharField(required=True, error_messages={'required': '场景描述为空'})
    # test_case_ids = serializers.CharField(required=True, error_messages={'required': '执行场景id列表为空'})
    reMark = serializers.CharField(required=False)


    class Meta:
        model = UiTestScene
        fields = ('model_name', 'fun_name', 'scene_name', 'scene_desc', 'reMark', 'update_user')


class TestSceneParamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UiSceneParams
        fields = ('param_dic', 'test_case_index_id', "sort")
