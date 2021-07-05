from django.db import models
from utils.basemodels import BaseModel
from account_system.models import UserProfile, Department

STATUS = (
    (1, '运行中'),
    (0, '已停止'),
)
OS_TYPE = (
    (0, 'windows server 2008'),
    (1, 'windows server 2012'),
    (2, 'windows 10'),
    (3, 'Centos 6'),
    (4, 'Centos 7'),
)

VM_STATUS = (
    (0, '闲置'),
    (1, '使用中')
)

VM_PURPOSE = (
    (0, '闲置'),
    (1, '开发环境'),
    (2, '测试环境'),
    (3, '自动化执行机')
)

TEST_PHASE = (
    (0, 'SIT'),
    (1, 'UAT'),
)

BROWSER_TYPE = (
    (0, 'chrome'),
    (1, 'firefox'),
    (2, 'ie')
)


class Server(BaseModel):
    # 服务器信息
    server_ip = models.CharField(default='', max_length=64,  verbose_name="服务器IP", blank=True, null=True)
    operating_system = models.IntegerField(default=4, choices=OS_TYPE, verbose_name='操作系统', blank=True, null=True)
    server_model = models.CharField(default='', max_length=64, verbose_name='服务器型号', blank=True, null=True,)
    server_cpu = models.IntegerField(default=0, verbose_name='服务器CPU（核）', blank=True, null=True,)
    server_memory = models.IntegerField(default=0, verbose_name='服务器内存（G）', blank=True, null=True,)
    server_disk = models.FloatField(default=0, verbose_name='服务器硬盘（T）', blank=True, null=True,)
    user_department = models.ForeignKey(Department, default='', verbose_name='使用部门', related_name='server_user_department', on_delete=models.SET_NULL, null=True, blank=True,)
    # user_department = models.ManyToManyField(DepartMent, blank=True, null=True)
    person_liable = models.ForeignKey(UserProfile, default='', verbose_name='管理责任人', related_name='servre_person_liable', on_delete=models.SET_NULL, null=True, blank=True,)
    # person_liable = models.ManyToManyField(UserProfile, blank=True, null=True)
    Usage_status = models.IntegerField(choices=STATUS, default=0, null=True, blank=True, verbose_name='使用状态')
    vm_num = models.IntegerField(default=0, null=True, blank=True, verbose_name='虚拟机数量')

    class Meta:
        db_table = 'server'
        ordering = ['-id']
        unique_together = ('server_ip', )


class VmServer(BaseModel):
    # 虚拟机信息
    server = models.ForeignKey(Server, related_name='vm_server', default='', null=True, blank=True, verbose_name='所属服务器', on_delete=models.SET_NULL)
    Virtual_machine_IP = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="虚拟机ip")
    Virtual_machine_username = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="虚拟机账号")
    Virtual_machine_password = models.TextField(default='', null=True, blank=True, verbose_name="虚拟机密码")
    Usage_status = models.IntegerField(default=0, choices=STATUS, verbose_name='使用状态', null=True, blank=True)
    Virtual_machine_status = models.IntegerField(default=0, choices=VM_STATUS, verbose_name='虚拟机状态', null=True, blank=True)
    entry_name = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="项目名称")
    project_manager = models.ForeignKey(UserProfile, default='', null=True, blank=True, verbose_name='项目经理', related_name='vm_project_manager', on_delete=models.SET_NULL)
    operating_system = models.IntegerField(default=3, choices=OS_TYPE, verbose_name='操作系统', null=True, blank=True)
    purpose = models.IntegerField(default=0, choices=VM_PURPOSE, verbose_name='虚拟机用途', null=True, blank=True,)
    Virtual_machine_CPU = models.IntegerField(default=0, null=True, blank=True, verbose_name='虚拟机CPU（核）')
    Virtual_machine_memory = models.IntegerField(default=0, null=True, blank=True, verbose_name='虚拟机内存（G）')
    Virtual_machine_hard_disk = models.IntegerField(default=0, null=True, blank=True, verbose_name='虚拟机硬盘（G）')
    person_liable = models.ForeignKey(UserProfile, default='', verbose_name='管理责任人', related_name='vm_person_liable', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'vmserver'
        ordering = ['-id']
        unique_together = ('Virtual_machine_IP', )


class TestVmWorker(BaseModel):
    # 测试执行机信息
    virtual_machine = models.ForeignKey(VmServer, default='', null=True, blank=True, related_name='test_workder_virtual_machine', verbose_name='虚拟机', on_delete=models.SET_NULL)
    cluster_name = models.CharField(default='', max_length=10, null=True, blank=True, verbose_name="集群名称")
    machine_description = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="虚拟机使用描述")
    testing_phase = models.IntegerField(default=0, choices=TEST_PHASE, null=True, blank=True, verbose_name="测试阶段")
    browser_type = models.IntegerField(default=0, choices=BROWSER_TYPE, null=True, blank=True, verbose_name="浏览器类型")
    browser_version = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="浏览器版本")
    test_owner = models.ForeignKey(UserProfile, default='', verbose_name='管理责任人', related_name='test_workder_owner', on_delete=models.SET_NULL, null=True, blank=True)
    max_parallel_task = models.IntegerField(default=2, null=True, blank=True, verbose_name='并行任务上限')

    class Meta:
        db_table = 'testvmworker'
        ordering = ['-id']
        unique_together = ('virtual_machine', )


# class UiTestTask(BaseModel):
#     # ui测试任务
#     test_worker =
#
