import json
import re
import time

from rest_framework import serializers

from account_system.models import UserProfile
from common.regular_ls import REGEX_IP
from system_settings.models import TaskControl, Environment, Project, PerformMachine, Dataexplain, DataDictionary, \
    MysqlInfo

# 项目信息管理
from zy_api_testing.models import Scene


class ProjectSerializerAdd(serializers.ModelSerializer):
    # 项目信息管理添加&修改 表单验证反序列化设置

    entry_name = serializers.CharField(required=True, error_messages={'required': '项目名称不能为空！'})
    project_manager = serializers.IntegerField(required=True, error_messages={'required': '项目经理不能为空！'})
    Test_Leader = serializers.IntegerField(required=True, error_messages={'required': '测试责任人不能为空！'})

    # Project_description = serializers.CharField(required=False)
    # , min_length=0, max_length=300,
    # error_messages={
    #     'min_length': '项目描述请输入0~300个字符！',
    #     'max_length': '项目描述请输入0~300个字符！'
    # })
    # remark = serializers.CharField(required=False)
    # , min_length=0, max_length=300,
    #  error_messages={
    #      'min_length': '备注请输入0~300个字符！',
    #      'max_length': '备注请输入0~300个字符！'
    #  })

    def validate_entry_name(self, entry_name):
        if Project.objects.filter(entry_name=entry_name) and not self.initial_data.get("id"):
            raise serializers.ValidationError('项目名称不能重复')
        return entry_name

    def validate_project_manager(self, project_manager):
        if not UserProfile.objects.filter(id=project_manager):
            raise serializers.ValidationError('项目经理不存在')
        return UserProfile.objects.filter(id=project_manager).first()

    def validate_Test_Leader(self, Test_Leader):
        if not UserProfile.objects.filter(id=Test_Leader):
            raise serializers.ValidationError('测试责任人不存在')
        return UserProfile.objects.filter(id=Test_Leader).first()

    class Meta:
        model = Project
        fields = ('entry_name', 'project_manager', 'Test_Leader', 'Project_description', 'remark')


class ProjectSerializerQuery(serializers.ModelSerializer):
    # 项目信息查询 表单验证 序列化
    entry_name = serializers.CharField()
    project_manager = serializers.SerializerMethodField()
    Test_Leader = serializers.SerializerMethodField()
    Project_description = serializers.CharField()
    remark = serializers.CharField()
    update_time = serializers.DateTimeField()
    create_time = serializers.DateTimeField()

    def get_project_manager(self, obj):
        if obj.project_manager:
            return obj.project_manager.Real_name
        else:
            return None

    def get_Test_Leader(self, obj):
        if obj.Test_Leader:
            return obj.Test_Leader.Real_name
        else:
            return None

    class Meta:
        model = Project
        fields = ('id', 'entry_name', 'project_manager', 'Test_Leader', 'Project_description', 'remark', 'create_time',
                  'update_time')


# 测试环境配置
class EnvironmentSerializerAdd(serializers.ModelSerializer):
    # 环境信息管理添加&修改 表单验证反序列化设置

    environmental_name = serializers.CharField(required=True, error_messages={'required': '环境名称不能为空！'})
    entry_name = serializers.IntegerField(required=True, error_messages={'required': '项目名称不能为空！'})
    Test_type = serializers.IntegerField(required=True, min_value=0, max_value=1,
                                         error_messages={'required': '测试类型 不能为空',
                                                         'min_value': '测试类型 请输入0-1之间的值',
                                                         'max_value': '测试类型 请输入0-1之间的值'})
    Testing_phase = serializers.IntegerField(required=True, min_value=0, max_value=3,
                                             error_messages={'required': '测试阶段 不能为空',
                                                             'min_value': '测试阶段 请输入0-3之间的值',
                                                             'max_value': '测试阶段 请输入0-3之间的值'})
    Test_address = serializers.CharField(required=True, error_messages={'required': '测试地址不能为空！'})
    Test_account = serializers.CharField(required=True, error_messages={'required': '测试账号不能为空！'})
    Test_password = serializers.CharField(required=True, error_messages={'required': '测试密码不能为空！'})

    # project_manager = serializers.IntegerField(required=True, error_messages={'required': '项目经理不能为空！'})
    # Test_Leader = serializers.IntegerField(required=True, error_messages={'required': '测试负责人不能为空！'})
    # remark = serializers.CharField(required=False, min_length=0, max_length=300,
    #                                 error_messages={
    #                                     'min_length': '备注请输入0~300个字符！',
    #                                     'max_length': '备注请输入0~300个字符！'
    #                                 })
    def validate_entry_name(self, entry_name):
        if not Project.objects.filter(id=entry_name):
            raise serializers.ValidationError('项目不存在')
        return Project.objects.filter(id=entry_name).first()

    def validate_environmental_name(self, environmental_name):
        if Environment.objects.filter(environmental_name=environmental_name) and not self.initial_data.get("id"):
            raise serializers.ValidationError('环境名称不能重复')
        return environmental_name

    def validate_Test_address(self, Test_address):
        regular = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if not re.match(regular, Test_address):
            raise serializers.ValidationError('测试地址格式错误')
        return Test_address

    def validate_Test_account(self, Test_account):
        regular = '([0-9a-zA-Z]|[$-_@.&+]){4,32}'
        if not re.match(regular, Test_account):
            raise serializers.ValidationError('测试账号格式错误')
        return Test_account

    def validate_Test_password(self, Test_password):
        regular = '([0-9a-zA-Z]|[$-_@.&+]){4,32}'
        if not re.match(regular, Test_password):
            raise serializers.ValidationError('测试密码格式错误')
        return Test_password

    # def validate_project_manager(self, project_manager):
    #     if not UserProfile.objects.filter(id=project_manager):
    #         raise serializers.ValidationError('项目经理不存在')
    #     return UserProfile.objects.filter(id=project_manager).first()
    #
    # def validate_Test_Leader(self, Test_Leader):
    #     if not UserProfile.objects.filter(id=Test_Leader):
    #         raise serializers.ValidationError('测试责任人不存在')
    #     return UserProfile.objects.filter(id=Test_Leader).first()

    class Meta:
        model = Environment
        fields = ('environmental_name', 'entry_name', 'Test_type', 'Testing_phase', 'Test_address', 'Test_account',
                  'Test_password', 'remark')


class EnvironmentSerializerQuery(serializers.ModelSerializer):
    # 测试环境信息 表单校验 序列化
    environmental_name = serializers.CharField()
    entry_name = serializers.SerializerMethodField()
    Test_type = serializers.SerializerMethodField()
    Testing_phase = serializers.SerializerMethodField()
    Test_address = serializers.CharField()
    Test_account = serializers.CharField()
    Test_password = serializers.CharField()
    # project_manager = serializers.SerializerMethodField()
    # Test_Leader = serializers.SerializerMethodField()
    remark = serializers.CharField()
    update_time = serializers.DateTimeField()
    create_time = serializers.DateTimeField()

    def get_entry_name(self, obj):
        if obj.entry_name:
            data = ProjectSerializerQuery(obj.entry_name).data
            return {
                'id': data.get('id'),
                'entry_name': data.get('entry_name'),
                'project_manager': data.get('project_manager'),
                'Test_Leader': data.get('Test_Leader'),
            }
        else:
            return None

    def get_Test_type(self, obj):
        return obj.get_Test_type_display()

    def get_Testing_phase(self, obj):
        return obj.get_Testing_phase_display()

    # def get_project_manager(self, obj):
    #     if obj.project_manager:
    #         return obj.project_manager.Real_name
    #     else:
    #         return None
    #
    # def get_Test_Leader(self, obj):
    #     if obj.Test_Leader:
    #         return obj.Test_Leader.Real_name
    #     else:
    #         return None

    class Meta:
        model = Environment
        fields = (
        'id', 'environmental_name', 'entry_name', 'Test_type', 'Testing_phase', 'Test_address', 'Test_account',
        'Test_password', 'remark', 'create_time', 'update_time')


class EnvironmentSerializerForeignQuery(serializers.ModelSerializer):
    # 测试环境信息 表单校验 序列化
    environmental_name = serializers.CharField()
    entry_name = serializers.SerializerMethodField()
    Test_address = serializers.CharField()

    # Test_type = serializers.CharField()
    # Testing_phase = serializers.CharField()
    # Test_address = serializers.CharField()
    # Test_account = serializers.CharField()
    # Test_password = serializers.CharField()
    # project_manager = serializers.CharField()
    # Test_Leader = serializers.CharField()
    # remarks = serializers.CharField()
    def get_entry_name(self, obj):
        if obj.entry_name:
            data = ProjectSerializerQuery(obj.entry_name).data
            return {
                'id': data.get('id'),
                'entry_name': data.get('entry_name'),
                'project_manager': data.get('project_manager'),
                'Test_Leader': data.get('Test_Leader'),
            }
        else:
            return None

    # def get_Testing_phase(self, obj):
    #     return obj.get_Testing_phase_display()
    #
    # def get_project_manager(self, obj):
    #     if obj.project_manager:
    #         return obj.project_manager.Real_name
    #     else:
    #         return None

    class Meta:
        model = Environment
        fields = ('id', 'environmental_name', 'entry_name', 'Test_address')


# 定时任务管理
class TaskSerializerQuery(serializers.ModelSerializer):
    # 反序列化
    job_type = serializers.SerializerMethodField()
    job_name = serializers.CharField()
    remark = serializers.CharField()
    environment = serializers.SerializerMethodField()
    cron_expression = serializers.CharField()
    mails = serializers.CharField()
    execute_type = serializers.CharField()
    execute_day = serializers.CharField()
    execute_log = serializers.CharField()

    def get_job_type(self, obj):
        return obj.get_job_type_display()

    def get_environment(self, obj):
        if obj.environment:
            data = EnvironmentSerializerForeignQuery(obj.environment)
            return data.data
        else:
            return None

    class Meta:
        model = TaskControl
        fields = ('id', 'job_type', 'job_name', 'environment', 'remark', 'cron_expression', 'mails', 'execute_type',
                  'execution_status', 'execute_day', 'expend_time', 'update_time', 'job_status', 'start_time',
                  'end_time', "execute_log")


class TaskSerializerAdd(serializers.ModelSerializer):
    # 添加&修改 表单验证 反序列化
    job_type = serializers.IntegerField(required=True, min_value=0, max_value=1,
                                        error_messages={'required': '任务类型 不能为空',
                                                        'min_value': '任务类型 请输入0-1之间的值',
                                                        'max_value': '任务类型 请输入0-1之间的值'})
    job_name = serializers.CharField(required=True, error_messages={'required': '任务名称 不能为空'})
    remark = serializers.CharField(required=False, min_length=1, max_length=100,
                                   error_messages={'min_value': '备注 请输入1-100长度的字符', 'max_length': '备注 请输入1~100个字符！'})
    method = serializers.CharField(required=True, error_messages={'required': '任务类型 不能为空'})
    end_cron_expression = serializers.CharField(required=False)
    environment = serializers.IntegerField(required=True, error_messages={'required': 'environment 不能为空'})
    performMachine = serializers.IntegerField(required=False, error_messages={'required': '执行机id 不能为空'})
    mails = serializers.CharField(required=False, min_length=8, max_length=255,
                                  error_messages={'min_value': '备注 请输入8-255长度的字符', 'max_length': '备注 请输入8~255个字符！'})
    execute_type = serializers.CharField(required=True, min_length=1, max_length=10,
                                         error_messages={'required': '执行周期 不能为空', 'min_value': '备注 请输入1-100长度的字符',
                                                         'max_length': '周期时间 请输入1~10个字符！'})
    # execute_day = serializers.CharField(required=False, min_length=1, max_length=10,
    #                                error_messages={'min_value': '备注 请输入1-100长度的字符', 'max_length': '周期日期 请输入1~10个字符！'})
    test_config = serializers.CharField(required=True, min_length=1, max_length=255,
                                        error_messages={'required': '执行场景id列表 不能为空', 'min_value': '备注 请输入3-255长度的字符',
                                                        'max_length': '备注 请输入3~255个字符！'})

    def validate_environment(self, environment):
        if not Environment.objects.filter(id=environment):
            raise serializers.ValidationError('Error "Environment", please check it')
        return Environment.objects.filter(id=environment).first()

    def validate_performMachine(self, performMachine):
        if (performMachine and not PerformMachine.objects.filter(id=performMachine) and not self.initial_data.get(
                "id")):
            raise serializers.ValidationError('执行机id Error!')
        return PerformMachine.objects.filter(id=performMachine).first()

    def validate_cron_expression(self, cron_expression):
        # try:  # 判断是否正确时间字符串
        #     time.strptime(cron_expression, "%Y-%m-%d %H:%M:%S")
        # except:
        #     raise serializers.ValidationError("时间格式不正确")
        # end_cron_expression = get_cron_expression(cron_expression, self.initial_data.get('execute_type'), self.initial_data.get('execute_day'))
        # cron_expression = '0|'+cron_expression
        return cron_expression

    def validate_end_cron_expression(self, end_cron_expression):
        # try:  # 判断是否正确时间字符串
        #     time.strptime(cron_expression, "%Y-%m-%d %H:%M:%S")
        # except:
        #     raise serializers.ValidationError("时间格式不正确")
        end_cron_expression = get_cron_expression(self.initial_data.get('cron_expression'),
                                                  self.initial_data.get('execute_type'),
                                                  self.initial_data.get('execute_day'))
        # cron_expression = '0|'+cron_expression
        return end_cron_expression

    def validate_mails(self, mails):
        if mails:
            mail_list = mails.split(';')
            for mail in mail_list:
                try:
                    if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', mail):
                        raise serializers.ValidationError("邮箱格式不正确 : {}".format(mail))
                except Exception as e:
                    raise serializers.ValidationError("邮箱格式不正确 : {}".format(mail))
        return mails

    def validate_test_config(self, test_config):
        test_config_id_list = json.loads(test_config)
        for test_config_id in test_config_id_list:
            if (self.initial_data.get("job_type") in [0, '0']) and not (Scene.objects.filter(id=test_config_id)):
                raise serializers.ValidationError('测试场景id错误:{}'.format(test_config_id))
        return test_config

    class Meta:
        model = TaskControl
        fields = (
        'id', 'job_type', 'job_name', 'environment', 'test_config', 'remark', 'cron_expression', 'end_cron_expression',
        'create_user', 'method', 'performMachine', 'mails', 'execute_type', 'execute_day')


def get_cron_expression(cron_expression, execute_type, execute_day):
    """
    params:
        cron_expression: 执行具体时间 0： ‘’  ， 1 ： ‘%H:%M:%S’  ， 2：‘%H:%M:%S’ ， 3：‘%H:%M:%S’  除立即执行外  其余周期类型传  时分秒 字符串 ex  '10:21:31'
        execute_type:   执行周期类型  0,1,2,3   立即执行/每天定点执行/每周定点执行/每月定点执行
        execute_day:    具体周期时间   0 : '', 1:'', 2:'1-7' , 3:‘1-31’
    """
    # cron_expression = '2|day_of_week='
    # cron_expression += str(data.get("week_day")) + "|hour="
    # cron_expression += str(data.get("remind_time"))[0:2] + "|minutes="
    # cron_expression += str(data.get("remind_time"))[3:5]
    # scheduler.add_job(autoReminder, 'cron', day_of_week=4, hour=18, minute=00, id='message_send')
    # scheduler.add_job(matterStatistics, 'cron', hour=23, minute=58, id='statistics_002')
    # task = scheduler.add_job(getattr(TaskJob, method), 'cron',
    #                          year=para_dict.get('year'), month=para_dict.get('month'), day=para_dict.get('day'),
    #                          week=para_dict.get('week'), day_of_week=para_dict.get('day_of_week'),
    #                          hour=para_dict.get('hour'), minute=para_dict.get('minutes'),
    #                          second=para_dict.get('second'), start_date=para_dict.get('start_date'),
    #                          end_date=para_dict.get('end_date'), id=str(task_id),
    #                          args=[])
    end_cron_expression = ''
    if execute_type == 1:
        end_cron_expression = '2|hour='
        end_cron_expression += cron_expression[0:2] + "|minutes="
        end_cron_expression += cron_expression[3:5]
        # end_cron_expression += cron_expression[3:5]+"|second="+cron_expression[6:8]

    if execute_type == 2:
        end_cron_expression = '2|day_of_week=' + str(execute_day) + '|hour='
        end_cron_expression += cron_expression[0:2] + "|minutes="
        end_cron_expression += cron_expression[3:5]
    if execute_type == 3:
        end_cron_expression = '2|month=*' + '|day=' + str(int(execute_day) + 1) + '|hour='
        end_cron_expression += cron_expression[0:2] + "|minutes="
        end_cron_expression += cron_expression[3:5]
        # 2|month=*|day=5|hour=13|minutes=07|second=58
    return end_cron_expression


# 执行机管理
class PerformMachineSerializerAdd(serializers.ModelSerializer):
    # 添加&修改 表单验证 反序列化
    perform_ip = serializers.CharField(required=True, error_messages={'required': '执行机ip 不能为空'})
    operating_system = serializers.IntegerField(required=True, min_value=0, max_value=4,
                                                error_messages={'required': '操作系统 不能为空',
                                                                'min_value': '操作系统 请输入0-4之间的值',
                                                                'max_value': '操作系统 请输入0-4之间的值'})
    java_version = serializers.CharField(required=True, error_messages={'required': 'java版本 不能为空'})
    browser_version = serializers.CharField(required=True, error_messages={'required': '浏览器版本 不能为空'})
    browser_type = serializers.IntegerField(required=True, min_value=0, max_value=2,
                                            error_messages={'required': '浏览器类型 不能为空',
                                                            'min_value': '浏览器类型 请输入0-2之间的值',
                                                            'max_value': '浏览器类型 请输入0-2之间的值'})
    entry_name = serializers.IntegerField(required=True, error_messages={'required': '项目id 不能为空'})

    def validate_entry_name(self, entry_name):
        if not Project.objects.filter(id=entry_name):
            raise serializers.ValidationError("该项目不存在")
        return Project.objects.filter(id=entry_name).first()

    def validate_Virtual_machine_IP(self, perform_ip):
        # 虚拟机ip字段验证
        if not re.match(REGEX_IP, perform_ip):
            raise serializers.ValidationError("执行机IP地址非法")
        return perform_ip

    class Meta:
        model = PerformMachine
        fields = ('id', 'perform_ip', 'operating_system', 'java_version', 'entry_name', 'browser_version',
                  'browser_type', 'machine_description', 'max_parallel_task', 'cluster_name', 'remark')


class PerformMachineSerializerQuery(serializers.ModelSerializer):
    perform_ip = serializers.CharField()
    operating_system = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    java_version = serializers.CharField()
    entry_name = serializers.SerializerMethodField()
    browser_version = serializers.CharField()
    browser_type = serializers.SerializerMethodField()
    machine_description = serializers.CharField()
    remark = serializers.CharField()
    update_time = serializers.DateTimeField()
    create_time = serializers.DateTimeField()

    def get_entry_name(self, obj):
        if obj.entry_name:
            data = ProjectSerializerQuery(obj.entry_name).data
            return {
                'id': data.get('id'),
                'entry_name': data.get('entry_name'),
                'project_manager': data.get('project_manager'),
                'Test_Leader': data.get('Test_Leader'),
            }
        else:
            return None

    def get_status(self, obj):
        return obj.get_status_display()

    def get_operating_system(self, obj):
        return obj.get_operating_system_display()

    def get_browser_type(self, obj):
        return obj.get_browser_type_display()

    class Meta:
        model = PerformMachine
        fields = ('id', 'perform_ip', 'operating_system', 'status', 'java_version', 'entry_name', 'browser_version',
                  'browser_type', 'machine_description', 'remark', 'create_time', 'update_time')


class DataDictionarySerializerQuery(serializers.ModelSerializer):
    class Meta:
        model = Dataexplain
        fields = ('id', 'dictionary_code', 'dictionary_explain')


class DataDictionarySerializerAdd(serializers.ModelSerializer):
    dictionary_code = serializers.CharField(required=True, min_length=1, max_length=100,
                                            error_messages={'min_value': '编号 请输入1-100长度的字符',
                                                            'max_length': '备注 请输入1~100个字符！'})
    dictionary_explain = serializers.CharField(required=True, min_length=1, max_length=100,
                                               error_messages={'min_value': '备注 请输入1-100长度的字符',
                                                               'max_length': '备注 请输入1~100个字符！'})

    def validate_dictionary_code(self, dictionary_code):
        if Dataexplain.objects.filter(dictionary_code=dictionary_code) and not self.initial_data.get("id"):
            raise serializers.ValidationError('字典编码不能重复')
        return dictionary_code

    class Meta:
        model = Dataexplain
        fields = ('id', 'dictionary_code', 'dictionary_explain')


class SonDataDictionarySerializerQuery(serializers.ModelSerializer):
    class Meta:
        model = DataDictionary
        fields = ('id', 'Dataexplain_id', 'DictionarySubitem_code', 'DictionarySubitem_explain', 'dictionary_item1',
                  'dictionary_item2', 'dictionary_item3', 'item_desc')


class SonDataDictionarySerializerAdd(serializers.ModelSerializer):
    Dataexplain_id = serializers.IntegerField(required=True, error_messages={'required': '父级数据字典id不能为空！'})
    DictionarySubitem_code = serializers.CharField(required=True, min_length=1, max_length=100,
                                                   error_messages={'min_value': '编号 1-100长度的字符',
                                                                   'max_length': '备注 请输入1~100个字符！'})
    DictionarySubitem_explain = serializers.CharField(required=True, min_length=1, max_length=100,
                                                      error_messages={'min_value': '备注 请输入1-100长度的字符',
                                                                      'max_length': '备注 请输入1~100个字符！'})

    def validate_DictionarySubitem_code(self, DictionarySubitem_code):
        if DataDictionary.objects.filter(DictionarySubitem_code=DictionarySubitem_code,
                                         Dataexplain_id=self.initial_data.get(
                                                 "Dataexplain_id")) and not self.initial_data.get("id"):
            raise serializers.ValidationError('同一父级字典项下 子字典编码不能重复')
        return DictionarySubitem_code

    def validate_Dataexplain_id(self, Dataexplain_id):
        if not Dataexplain.objects.filter(id=Dataexplain_id):
            raise serializers.ValidationError('父字典id不存在')
        return Dataexplain.objects.filter(id=Dataexplain_id).first()

    class Meta:
        model = DataDictionary
        fields = ('id', 'Dataexplain_id', 'DictionarySubitem_code', 'DictionarySubitem_explain', 'dictionary_item1',
                  'dictionary_item2', 'dictionary_item3', 'item_desc')


class MysqlInfoSerializerAdd(serializers.ModelSerializer):
    host = serializers.CharField(required=True, error_messages={'required': 'ip地址不能为空！'})
    port = serializers.IntegerField(required=True, error_messages={'required': '端口号不能为空！'})
    user = serializers.CharField(required=True, error_messages={'required': '账户不能为空！'})
    password = serializers.CharField(required=True, error_messages={'required': '密码不能为空！'})
    table_name = serializers.CharField(required=True, error_messages={'required': '数据库不能为空！'})
    connect_name = serializers.CharField(required=True, error_messages={'required': '链接名不能为空！'})

    def validate_host(self, host):
        if not re.match(REGEX_IP, host):
            raise serializers.ValidationError("IP地址 非法")
        return host

    def validate_port(self, port):
        try:
            port = int(port)
            return port
        except Exception as _:
            raise serializers.ValidationError("端口号 非法")

    class Meta:
        model = MysqlInfo
        fields = ('id', 'host', 'port', 'user', 'password', 'table_name', 'connect_name', 'remark')


class MysqlInfoSerializerQuery(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = MysqlInfo
        fields = ('id', 'host', 'port', 'user', 'password', 'table_name', 'connect_name', 'remark', 'status')


class MysqlInfoDropDownBoxSerializerQuery(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = MysqlInfo
        fields = ('id', 'connect_name', 'status')
