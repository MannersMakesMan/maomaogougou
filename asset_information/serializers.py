import re
import base64

from rest_framework import serializers

from asset_information.models import Server, VmServer, TestVmWorker
from common.regular_ls import REGEX_IP
from account_system.models import UserProfile, Department


class ServerSerializerAdd(serializers.ModelSerializer):
    # 服务器 添加&修改 表单验证 反序列化
    server_ip = serializers.CharField(required=True, error_messages={'required': '服务器IP地址 不能为空'})
    operating_system = serializers.IntegerField(required=False, min_value=0, max_value=4,
                                  error_messages={'min_value': '操作系统 请输入0-4之间的值',
                                                  'max_value': '操作系统 请输入0-4之间的值'})
    server_model = serializers.CharField(required=False, min_length=0, max_length=20,
                                        error_messages={'max_length': '服务器型号 不能大于20个字符'})
    server_cpu = serializers.IntegerField(required=False, min_value=0, max_value=100,
                                   error_messages={'min_value': '服务器CPU（核） 请输入0-1000之间的值',
                                                   'max_value': '服务器CPU（核） 请输入0-1000之间的值'})
    server_memory = serializers.IntegerField(required=False, min_value=0, max_value=100,
                                      error_messages={'min_value': '服务器内存（G） 请输入0-1000之间的值',
                                                      'max_value': '服务器内存（G） 请输入0-1000之间的值'})
    server_disk = serializers.FloatField(required=False, min_value=0, max_value=100,
                                    error_messages={'min_value': '服务器硬盘（T） 请输入0-1000之间的值',
                                                    'max_value': '服务器硬盘（T） 请输入0-1000之间的值'})
    user_department = serializers.IntegerField(required=True, error_messages={'required': '使用部门 不能为空'})
    person_liable = serializers.IntegerField(required=True, error_messages={'required': '管理责任人 不能为空'})

    def validate_server_ip(self, server_ip):
        # 反序列化 字段正则验证
        if not re.match(REGEX_IP, server_ip):
            raise serializers.ValidationError("服务器IP地址 非法")
        return server_ip

    def validate_user_department(self, user_department):
        # 反序列化 外键表单验证
        try:
            department = Department.objects.get(id=user_department)
            return department
        except:
            raise serializers.ValidationError("没有此部门")

    def validate_person_liable(self, person_liable):
        try:
            user = UserProfile.objects.get(id=person_liable)
            return user
        except:
            raise serializers.ValidationError("没有此用户")

    class Meta:
        model = Server
        fields = ('server_ip', 'operating_system', 'server_model', 'server_cpu', 'server_memory', 'server_disk', 'user_department', 'person_liable')


class ServerSerializerQuery(serializers.ModelSerializer):
    # 服务器查询 表单验证 序列化
    server_ip = serializers.CharField()
    operating_system = serializers.SerializerMethodField()
    server_model = serializers.CharField()
    server_cpu = serializers.IntegerField()
    server_memory = serializers.IntegerField()
    server_disk = serializers.FloatField()
    user_department = serializers.SerializerMethodField()
    person_liable = serializers.SerializerMethodField()
    Usage_status = serializers.SerializerMethodField()
    update_time = serializers.DateTimeField()
    vm_num = serializers.IntegerField()
    remark = serializers.CharField()

    def get_operating_system(self, obj):
        # 序列化情况下 取choice值
        return obj.get_operating_system_display()

    def get_Usage_status(self, obj):
        return obj.get_Usage_status_display()

    def get_user_department(self, obj):
        # 序列化情况下 取外键字段
        if obj.user_department:
            return obj.user_department.department_name
        else:
            return None

    def get_person_liable(self, obj):
        if obj.person_liable:
            return obj.person_liable.Real_name
        return None

    class Meta:
        model = Server
        fields = ('id', 'server_ip', 'operating_system', 'server_model', 'server_cpu', 'server_memory', 'server_disk', 'user_department', 'person_liable', 'remark', 'vm_num', 'update_time', 'Usage_status')

class VmSerializerAdd(serializers.ModelSerializer):
    # 虚拟机添加&修改 表单验证 反序列化
    server = serializers.IntegerField(required=True, error_messages={'required': '所属服务器IP 不能为空'})
    Virtual_machine_IP = serializers.CharField(required=True, error_messages={'required': '虚拟机ip 不能为空'})
    Virtual_machine_username = serializers.CharField(required=True, min_length=1, max_length=10, error_messages={'required': '虚拟机账号 不能为空',
                                                                                                                 'min_value': '虚拟机账号 请输入1-10长度的字符',
                                                                                                                 'max_value': '虚拟机账号 请输入1-10长度的字符'})
    Virtual_machine_password = serializers.CharField(required=True, error_messages={'required': '虚拟机密码 不能为空'})
    entry_name = serializers.CharField(required=False, min_length=1, max_length=20, error_messages={'min_value': '项目名称 请输入1-20长度的字符',
                                                                                                     'max_value': '项目名称 请输入1-20长度的字符'})
    project_manager = serializers.IntegerField(required=False)
    operating_system = serializers.IntegerField(required=True, min_value=0, max_value=4, error_messages={'required': '操作系统 不能为空',
                                                                                                         'min_value': '操作系统 请输入0-4之间的值',
                                                                                                         'max_value': '操作系统 请输入0-4之间的值'})
    purpose = serializers.IntegerField(required=True, min_value=0, max_value=3, error_messages={'required': '虚拟机用途 不能为空',
                                                                                                 'min_value': '虚拟机用途 请输入0-3之间的值',
                                                                                                 'max_value': '虚拟机用途 请输入0-3之间的值'})
    Virtual_machine_CPU = serializers.IntegerField(required=True, min_value=0, max_value=100, error_messages={'required': '虚拟机CPU（核） 不能为空',
                                                                                                              'min_value': '虚拟机CPU（核） 请输入0-100之间的值',
                                                                                                              'max_value': '虚拟机CPU（核） 请输入0-100之间的值'})

    Virtual_machine_memory = serializers.IntegerField(required=True, min_value=0, max_value=100,
                                             error_messages={'required': '虚拟机内存（G） 不能为空',
                                                             'min_value': '虚拟机内存（G） 请输入0-1000之间的值',
                                                             'max_value': '虚拟机内存（G） 请输入0-1000之间的值'})
    Virtual_machine_hard_disk = serializers.IntegerField(required=True, min_value=0, max_value=10000,
                                         error_messages={'required': '虚拟机硬盘（G） 不能为空',
                                                         'min_value': '虚拟机硬盘（G） 请输入0-10000之间的值',
                                                         'max_value': '虚拟机硬盘（G） 请输入0-10000之间的值'})
    person_liable = serializers.IntegerField(required=True, error_messages={'required': '管理责任人 不能为空'})


    def validate_Virtual_machine_IP(self, Virtual_machine_IP):
        # 虚拟机ip字段验证
        if not re.match(REGEX_IP, Virtual_machine_IP):
            raise serializers.ValidationError("虚拟机IP地址非法")
        return Virtual_machine_IP

    def validate_server(self, server):
        # 所属服务器验证
        try:
            server_obj = Server.objects.get(id=server)
            server_obj.vm_num += 1
            server_obj.save()
            return server_obj
        except:
            raise serializers.ValidationError("没有此服务器")

    def validate_Virtual_machine_password(self, Virtual_machine_password):
        # 虚拟机密码验证
        try:
            base64.b64decode(Virtual_machine_password)
            return Virtual_machine_password
        except:
            raise serializers.ValidationError("密码解码错误")

    def validate_project_manager(self, project_manager):
        # 项目经理验证
        try:
            user = UserProfile.objects.get(id=project_manager)
            return user
        except:
            raise serializers.ValidationError("没有此用户")

    def validate_person_liable(self, person_liable):
        # 管理责任人验证
        try:
            user = UserProfile.objects.get(id=person_liable)
            return user
        except:
            raise serializers.ValidationError("没有此用户")


    class Meta:
        model = VmServer
        fields = ('server', 'Virtual_machine_IP', 'Virtual_machine_username', 'Virtual_machine_password', 'entry_name', 'project_manager', 'operating_system', 'purpose',
                  'Virtual_machine_CPU', 'Virtual_machine_memory', 'Virtual_machine_hard_disk', 'person_liable')


class VmSerializerQuery(serializers.ModelSerializer):
    # 虚拟机查询 表单验证 序列化
    server = serializers.SerializerMethodField()
    Virtual_machine_IP = serializers.CharField()
    Virtual_machine_username = serializers.CharField()
    Virtual_machine_password = serializers.CharField()
    entry_name = serializers.CharField()
    project_manager = serializers.SerializerMethodField()
    operating_system = serializers.SerializerMethodField()
    purpose = serializers.SerializerMethodField()
    Virtual_machine_CPU = serializers.IntegerField()
    Virtual_machine_memory = serializers.IntegerField()
    Virtual_machine_hard_disk = serializers.IntegerField()
    person_liable = serializers.SerializerMethodField()
    update_time = serializers.DateTimeField()
    Usage_status = serializers.SerializerMethodField()
    Virtual_machine_status = serializers.SerializerMethodField()

    def get_server(self, obj):
        if obj.server:
            return obj.server.server_ip
        else:
            return None

    def get_project_manager(self, obj):
        if obj.project_manager:
            return obj.project_manager.Real_name
        else:
            return None

    def get_operating_system(self, obj):
        return obj.get_operating_system_display()

    def get_purpose(self, obj):
        return obj.get_purpose_display()

    def get_person_liable(self, obj):
        if obj.person_liable:
            return obj.person_liable.Real_name
        else:
            return None

    def get_Usage_status(self, obj):
        return obj.get_Usage_status_display()

    def get_Virtual_machine_status(self, obj):
        return obj.get_Virtual_machine_status_display()

    class Meta:
        model = VmServer
        fields = ('id', 'server', 'Virtual_machine_IP', 'Virtual_machine_username', 'Virtual_machine_password', 'entry_name', 'project_manager', 'operating_system', 'purpose',
                  'Virtual_machine_CPU', 'Virtual_machine_memory', 'Virtual_machine_hard_disk', 'person_liable', 'update_time', 'Usage_status', 'Virtual_machine_status')

class VmTestWorkerSerializerAdd(serializers.ModelSerializer):
    # 执行机 添加&修改 表单验证 序列化
    virtual_machine = serializers.IntegerField(required=True, error_messages={'required': '虚拟机id 不能为空'})
    cluster_name = serializers.CharField(required=True, min_length=1, max_length=20, error_messages={'required': '所属集群 不能为空',
                                                                                                     'min_value': '所属集群 请输入1-20长度的字符',
                                                                                                     'max_value': '所属集群 请输入1-20长度的字符'})
    machine_description = serializers.CharField(required=True, min_length=1, max_length=64, error_messages={'required': '执行机使用描述 不能为空',
                                                                                                            'min_value': '执行机使用描述 请输入1-64长度的字符',
                                                                                                            'max_value': '执行机使用描述 请输入1-64长度的字符'})
    testing_phase = serializers.IntegerField(required=True, min_value=0, max_value=1, error_messages={'required': '测试阶段 不能为空',
                                                                                                      'min_value': '测试阶段 请输入0-1之间的值',
                                                                                                      'max_value': '测试阶段 请输入0-1之间的值'})
    browser_type = serializers.IntegerField(required=True, min_value=0, max_value=2, error_messages={'required': '浏览器类型 不能为空',
                                                                                                     'min_value': '浏览器类型 请输入0-2之间的值',
                                                                                                     'max_value': '浏览器类型 请输入0-2之间的值'})
    browser_version = serializers.CharField(required=True, min_length=1, max_length=20, error_messages={'required': '浏览器版本 不能为空',
                                                                                                        'min_value': '浏览器版本 请输入1-20长度的字符',
                                                                                                        'max_value': '浏览器版本 请输入1-20长度的字符'})
    test_owner = serializers.IntegerField(required=True, error_messages={'required': '管理责任人 不能为空'})
    max_parallel_task = serializers.IntegerField(required=True, min_value=0, max_value=10, error_messages={'required': '并行任务上限 不能为空',
                                                                                                           'min_value': '并行任务上限 请输入0-10之间的值',
                                                                                                           'max_value': '并行任务上限 请输入0-10之间的值'})

    def validate_virtual_machine(self, virtual_machine):
        # 所属服务器验证
        try:
            vm_server_obj = VmServer.objects.get(id=virtual_machine)
            return vm_server_obj
        except:
            raise serializers.ValidationError("没有此虚拟机")

    def validate_test_owner(self, test_owner):
        # 管理责任人验证
        try:
            user = UserProfile.objects.get(id=test_owner)
            return user
        except:
            raise serializers.ValidationError("没有此用户")

    class Meta:
        model = TestVmWorker
        fields = ("virtual_machine", "cluster_name", "machine_description", "testing_phase", "browser_type", "browser_version", "test_owner", "max_parallel_task")


class UserLsSerializer(serializers.ModelSerializer):
    # 查询全部用户 id&姓名
    class Meta:
        model = UserProfile
        fields = ("id", "Real_name")


class DepartMentLsSerializer(serializers.ModelSerializer):
    # 查询全部团队 id&姓名
    class Meta:
        model = Department
        fields = ("id", "department_name")


class ServerSerializer(serializers.ModelSerializer):
    # 查询全部服务器 id&ip
    class Meta:
        model = Server
        fields = ("id", "server_ip")

