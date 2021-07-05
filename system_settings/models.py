from django.db import models

from account_system.models import UserProfile
from asset_information.models import VmServer, OS_TYPE, STATUS
from test_exe_conf.models import UiTestConfig
from utils.basemodels import BaseModel

Test_type = (
    (0, 'UI自动化测试'),
    (1, 'API自动化测试'),
)

Testing_phase = (
    (0, 'UT测试'),
    (1, 'SIT测试'),
    (2, 'UAT测试'),
    (3, '生产验收')
)

Task_period_type = (
    (0, '立即执行'),
    (1, '每天定点执行'),
    (2, '每周定点执行'),
    (3, '每月定点执行')
)

BROWSER_TYPE = (
    (0, 'chrome'),
    (1, 'firefox'),
    (2, 'ie')
)

JOB_TYPE = (
    (0, 'api自动化测试'),
    (1, 'ui自动化测试')
)

mysql_status = (
    (0, '链接失败'),
    (1, '链接成功')
)


# 项目信息管理
class Project(models.Model):
    entry_name = models.CharField(default='', max_length=64, blank=True, null=True, verbose_name='项目名称')
    project_manager = models.ForeignKey(UserProfile, default='', null=True, blank=True, verbose_name='项目经理', related_name='project_manager', on_delete=models.SET_NULL)
    Test_Leader = models.ForeignKey(UserProfile, default='', null=True, blank=True, verbose_name='测试责任人', related_name='Test_Leader', on_delete=models.SET_NULL)
    Project_description = models.CharField(default='', max_length=300, blank=True, null=True, verbose_name='项目描述')
    remark = models.TextField(default='', null=True, blank=True, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'project'
        ordering = ['-id']
        unique_together = ('entry_name', )


# 测试环境配置
class Environment(models.Model):
    environmental_name = models.CharField(default='', max_length=64, blank=True, null=True, verbose_name='环境名称')
    entry_name = models.ForeignKey(Project, default='', blank=True, null=True, verbose_name='项目名称', related_name='project_info', on_delete=models.SET_NULL)
    Test_type = models.IntegerField(choices=Test_type, default=0, null=True, blank=True, verbose_name='测试类型')
    Testing_phase = models.IntegerField(choices=Testing_phase, default=0, null=True, blank=True, verbose_name='测试阶段')
    Test_address = models.CharField(default='', max_length=1000, blank=True, null=True, verbose_name='测试地址信息')
    Test_account = models.CharField(default='', max_length=64, blank=True, null=True, verbose_name='测试账号')
    Test_password = models.CharField(default='', max_length=66, blank=True, null=True, verbose_name='测试密码')
    # project_manager = models.ForeignKey(UserProfile, default='', null=True, blank=True, verbose_name='项目经理', related_name='env_project_manager', on_delete=models.SET_NULL)
    # Test_Leader = models.ForeignKey(UserProfile, default='', null=True, blank=True, verbose_name='测试责任人', related_name='env_Test_Leader', on_delete=models.SET_NULL)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    remark = models.TextField(default='', null=True, blank=True, verbose_name='备注')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'Environment'
        ordering = ['-id']
        unique_together = ('environmental_name', )


# 执行机管理
class PerformMachine(models.Model):
    # 测试执行机信息
    perform_ip = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="执行机ip")
    operating_system = models.IntegerField(default=3, choices=OS_TYPE, verbose_name='操作系统', null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name='执行机状态', null=True, blank=True, choices=STATUS)
    java_version = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="java版本")
    entry_name = models.ForeignKey(Project, default='', blank=True, null=True, verbose_name='项目名称', related_name='PerformMachine_entry_name', on_delete=models.SET_NULL)
    browser_version = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="浏览器版本")
    browser_type = models.IntegerField(default=0, choices=BROWSER_TYPE, null=True, blank=True, verbose_name="浏览器类型")
    machine_description = models.CharField(default='', max_length=64, null=True, blank=True, verbose_name="执行机使用描述")
    max_parallel_task = models.IntegerField(default=2, null=True, blank=True, verbose_name='并行任务上限')
    cluster_name = models.CharField(default='', max_length=10, null=True, blank=True, verbose_name="集群名称")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    remark = models.TextField(default='', null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'PerformMachine'
        ordering = ['-id']
        unique_together = ('perform_ip', )


# 定时任务管理
class TaskControl(models.Model):
    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='任务id')
    job_type = models.IntegerField(default=0, choices=JOB_TYPE, verbose_name='任务类型 0/1   api/ui', null=True, blank=True)
    job_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='任务名称')
    job_status = models.CharField(max_length=50, blank=True, null=True, verbose_name='任务状态')
    environment = models.ForeignKey(Environment, default='', verbose_name='测试环境id', null=True, blank=True, on_delete=models.SET_NULL)
    performMachine = models.ForeignKey(PerformMachine, default='', verbose_name='执行机id', null=True, blank=True, on_delete=models.SET_NULL)
    test_config = models.CharField(max_length=251, blank=True, null=True,  verbose_name='测试配置id')
    method = models.CharField(default='', max_length=100, blank=True, null=True, verbose_name="定时任务调用方法")
    state = models.IntegerField(blank=True, null=True, verbose_name='任务是否需要启动标识')
    remark = models.CharField(max_length=1000, blank=True, null=True, verbose_name='责任人')
    cron_expression = models.CharField(max_length=200, blank=True, null=True, verbose_name='任务执行时间字符串')
    execute_type = models.CharField(max_length=10, blank=True, null=True, verbose_name='执行周期类型')
    execute_day = models.CharField(max_length=10, blank=True, null=True, verbose_name='执行周期日期')
    end_cron_expression = models.CharField(max_length=200, blank=True, null=True, verbose_name='任务执行配置字符串')
    create_user = models.CharField(max_length=200, blank=True, null=True, verbose_name='测试责任人/定时任务创建人')
    update_user = models.CharField(max_length=200, blank=True, null=True, verbose_name='任务修改人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间', null=True, blank=True)
    start_time = models.CharField(verbose_name='任务开始执行', max_length=200, null=True, blank=True)
    expend_time = models.CharField(verbose_name='任务执行耗时', max_length=200, null=True, blank=True)
    end_time = models.CharField(verbose_name='任务执行结束时间', max_length=200, null=True, blank=True)
    mails = models.CharField(max_length=255, blank=True, null=True, verbose_name='测试结果发送邮箱')
    execution_status = models.CharField(max_length=50, blank=True, null=True, verbose_name='执行状态')
    execute_log = models.TextField(blank=True, null=True, verbose_name='执行日志')

    class Meta:
        db_table = 'task_control'
        ordering = ['-id']
        # unique_together = ('job_name',)


# 数据字典管理
class Dataexplain(models.Model):
    dictionary_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='字典项编码')
    dictionary_explain = models.CharField(max_length=128, blank=True, null=True, verbose_name='字典项说明')

    class Meta:
        db_table = 'data_explain'
        ordering = ['-id']
        unique_together =('dictionary_code',)


class DataDictionary(models.Model):
    id = models.AutoField(primary_key=True)
    Dataexplain_id = models.ForeignKey(Dataexplain, default='', verbose_name='字典项外键', null=True, blank=True, on_delete=models.SET_NULL)
    DictionarySubitem_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='字典子项编码')
    DictionarySubitem_explain = models.CharField(max_length=128, blank=True, null=True, verbose_name='字典子项说明')
    dictionary_item1 = models.CharField(max_length=128, blank=True, null=True, verbose_name='字典项参数1')
    dictionary_item2 = models.CharField(max_length=128, blank=True, null=True, verbose_name='字典项参数2')
    dictionary_item3 = models.CharField(max_length=128, blank=True, null=True, verbose_name='字典项参数3')
    item_desc = models.CharField(max_length=128, blank=True, null=True, verbose_name='字典子项参数说明')

    class Meta:
        db_table = 'data_dictionary'
        ordering = ['-id']


class MysqlInfo(models.Model):
    host = models.CharField(verbose_name='数据库地址', max_length=32, null=True, blank=True)
    port = models.IntegerField(verbose_name='数据库端口号', null=True, blank=True)
    user = models.CharField(verbose_name='账号', max_length=32, null=True, blank=True)
    password = models.CharField(verbose_name='密码', max_length=32, null=True, blank=True)
    table_name = models.CharField(verbose_name='数据库名', max_length=32, null=True, blank=True)
    connect_name = models.CharField(verbose_name='链接名', max_length=32, null=True, blank=True)
    status = models.IntegerField(choices=mysql_status, verbose_name='数据库端口号', null=True, blank=True)
    remark = models.CharField(verbose_name='备注', max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'mysql_info'
        ordering = ['-id']
        unique_together = ('connect_name', )

