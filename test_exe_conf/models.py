from __future__ import unicode_literals

from django.db import models
from utils.basemodels import BaseModel
# Create your models here.
from django.contrib.auth.models import User

TESTSTATUS_CHOICE = (
    (0, '未开始'),
    (1, '执行中'),
    (2, '执行成功'),
    (3, '执行失败'),
)


class UiTestConfig(models.Model):
    # UI测试场景
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=32, blank=True, null=True)
    model_name = models.CharField(verbose_name='模块名称', max_length=32, blank=True, null=True)
    function_name = models.CharField(verbose_name='功能名称', max_length=32, blank=True, null=True)
    scene_name = models.CharField(verbose_name='场景名称', max_length=32, blank=True, null=True)
    scene_desc = models.CharField(verbose_name='场景描述', max_length=100, blank=True, null=True)
    method = models.TextField(verbose_name='调用方法', max_length=1000, blank=True, null=True)
    method_py_path = models.TextField(default='', verbose_name='调用方法的文件路径', max_length=1000, blank=True, null=True)
    method_id_ls = models.CharField(verbose_name='场景描述', max_length=1000, blank=True, null=True)
    method_remark = models.TextField(verbose_name='调用方法描述', max_length=1000, blank=True, null=True)
    build_user = models.CharField(verbose_name='创建人', max_length=32, blank=True, null=True)
    teststatus = models.IntegerField(choices=TESTSTATUS_CHOICE, verbose_name='测试结果', default=0)
    exe_log = models.TextField(max_length=1000, verbose_name='测试执行日志', blank=True, null=True)
    test_report = models.CharField(verbose_name='测试执行报告', max_length=100, blank=True, null=True)
    exe_time = models.DateTimeField(blank=True, null=True, verbose_name='上次执行时间')

    def __unicode__(self):
        return self.name

    class Meta:
        # managed = False
        # abstract = True
        db_table = 'ui_test_config'


class ApiTestConfig(models.Model):
    # api测试场景
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=32, blank=True, null=True)
    model_name = models.CharField(verbose_name='模块名称', max_length=32, blank=True, null=True)
    function_name = models.CharField(verbose_name='功能名称', max_length=32, blank=True, null=True)
    scene_name = models.CharField(verbose_name='场景名称', max_length=32, blank=True, null=True)
    scene_desc = models.CharField(verbose_name='场景描述', max_length=100, blank=True, null=True)
    method = models.TextField(verbose_name='调用方法', max_length=1000, blank=True, null=True)
    method_py_path = models.TextField(default='', verbose_name='调用方法的文件路径', max_length=3000, blank=True, null=True)
    method_id_ls = models.CharField(verbose_name='场景描述', max_length=1000, blank=True, null=True)
    method_remark = models.TextField(verbose_name='调用方法描述', max_length=1000, blank=True, null=True)
    build_user = models.CharField(verbose_name='创建人', max_length=32, blank=True, null=True)
    teststatus = models.IntegerField(choices=TESTSTATUS_CHOICE, verbose_name='测试结果', default=0)
    exe_log = models.TextField(max_length=1000, verbose_name='测试执行日志', blank=True, null=True)
    test_report = models.CharField(verbose_name='测试执行报告', max_length=100, blank=True, null=True)
    exe_time = models.DateTimeField(blank=True, null=True, verbose_name='上次执行时间')

    def __unicode__(self):
        return self.name

    class Meta:
        # managed = False
        # abstract = True
        db_table = 'api_test_config'


class UiTestReport(models.Model):
    # API&UI测试报告
    id = models.AutoField(primary_key=True)
    file_path = models.CharField(verbose_name='测试报告路径', max_length=100, blank=True, null=True)
    file_name = models.CharField(verbose_name='测试报告名称', max_length=100, blank=True, null=True, db_index=True)
    action_time = models.DateTimeField(blank=True, null=True, verbose_name='上次执行时间')
    test_type = models.CharField(blank=True, null=True, max_length=100, verbose_name='测试类型')
    spend_time = models.CharField(blank=True, null=True, max_length=20, verbose_name='测试执行时间')
    tester = models.CharField(verbose_name='测试执行人', max_length=20, blank=True, null=True)
    result = models.CharField(verbose_name='测试结果', max_length=20, blank=True, null=True)
    text_content = models.TextField(verbose_name='html内容', blank=True, null=True)

    class Meta:
        # managed = False
        # abstract = True
        db_table = 'ui_test_report'


class ApiTestReport(models.Model):
    # API&UI测试报告
    id = models.AutoField(primary_key=True)
    file_path = models.CharField(verbose_name='测试报告路径', max_length=120, blank=True, null=True)
    file_name = models.CharField(verbose_name='测试报告名称', max_length=100, blank=True, null=True, db_index=True)
    action_time = models.DateTimeField(blank=True, null=True, verbose_name='上次执行时间')
    test_type = models.CharField(blank=True, null=True, max_length=100, verbose_name='测试类型')
    spend_time = models.CharField(blank=True, null=True, max_length=20, verbose_name='测试执行时间')
    tester = models.CharField(verbose_name='测试执行人', max_length=20, blank=True, null=True)
    result = models.CharField(verbose_name='测试结果', max_length=20, blank=True, null=True)
    text_content = models.TextField(verbose_name='html内容', blank=True, null=True)

    class Meta:
        # managed = False
        # abstract = True
        db_table = 'api_test_report'
