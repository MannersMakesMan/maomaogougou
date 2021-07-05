from rest_framework import serializers
from test_exe_conf.models import UiTestConfig, ApiTestConfig, UiTestReport, ApiTestReport


class UiTestConfigSerializers(serializers.ModelSerializer):
    """
    ui测试场景 增加 查询
    """
    class Meta:
        model = UiTestConfig
        # fields = ('id')
        fields = ('name', 'model_name', 'function_name', 'scene_name', 'scene_desc', 'method', 'build_user', 'method_remark', 'method_id_ls', 'method_py_path')

class UiTestConfigListSerializers(serializers.ModelSerializer):
    """
    ui测试场景列表页
    """
    class Meta:
        model = UiTestConfig
        # fields = ('id')
        fields = ('id', 'name', 'model_name', 'function_name', 'scene_name', 'scene_desc', 'method', 'build_user', 'teststatus', 'method_id_ls', 'exe_time', 'method_py_path', 'exe_log')


class ApiTestConfigSerializers(serializers.ModelSerializer):
    """
    API测试场景 增加
    """
    class Meta:
        model = ApiTestConfig
        # fields = ('id')
        fields = ('name', 'model_name', 'function_name', 'scene_name', 'scene_desc', 'method', 'build_user', 'method_remark', 'method_id_ls')

class ApiTestConfigListSerializers(serializers.ModelSerializer):
    """
    API测试场景列表页
    """
    class Meta:
        model = ApiTestConfig
        # fields = ('id')
        fields = ('id', 'name', 'model_name', 'function_name', 'scene_name', 'scene_desc', 'method', 'build_user','teststatus', 'method_id_ls', 'exe_time')

class UiTestReportSerializers(serializers.ModelSerializer):
    """
    UI 测试报告
    """
    class Meta:
        model = UiTestReport
        fields = ('file_path', 'file_name', 'action_time', 'spend_time', 'tester', 'result', 'text_content', 'test_type')


class UiTestReportSerializersQuery(serializers.ModelSerializer):
    """
    UI 测试报告查询
    """
    class Meta:
        model = UiTestReport
        fields = ('file_path', 'file_name', 'action_time', 'spend_time', 'tester', 'result', 'test_type')

class ApiTestReportSerializersQuery(serializers.ModelSerializer):
    """
    API 测试报告查询
    """
    class Meta:
        model = UiTestReport
        fields = ('file_path', 'file_name', 'action_time', 'spend_time', 'tester', 'result', 'test_type')


class ApiTestReportSerializers(serializers.ModelSerializer):
    """
    API 测试报告
    """
    class Meta:
        model = ApiTestReport
        fields = ('id', 'file_name', 'action_time', 'spend_time', 'tester', 'result', 'text_content', 'test_type')
