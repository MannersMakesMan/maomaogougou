from django.db import models

from utils.basemodels import BaseModel

is_common_function = (
    (1, '公共方法'),
    (0, '非公共方法'),
)

is_need_value = (
    (1, '需要传递参数'),
    (0, '不需要传递参数')
)

is_need_button = (
    (1, '需要定位'),
    (0, '不需要定位')
)

is_need_assert = (
    (1, '需要断言'),
    (0, '不需要断言')
)

is_need_mysql = (
    (1, '需要数据库'),
    (0, '不需要数据库')
)

model_leval = (
    (1, '模块'),
    (0, '页面')
)


class CommonParams(models.Model):
    # UI测试 公共参数
    id = models.AutoField(primary_key=True)
    entry_name_id = models.CharField(verbose_name='项目id', max_length=32, blank=True, null=True)
    param_desc = models.CharField(verbose_name='参数名称', max_length=150, blank=True, null=True)
    param_value = models.CharField(verbose_name='参数值', max_length=200, blank=True, null=True)
    update_user = models.CharField(verbose_name='更新人', max_length=32, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    remark = models.CharField(verbose_name='备注', max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ("param_desc",)
        index_together = ("param_desc", )
        db_table = 'common_params'


class TestAppModel(models.Model):
    # UI测试模块-界面
    id = models.AutoField(primary_key=True)
    super_id = models.IntegerField(verbose_name='上级id', blank=True, null=True)
    # super_id = models.CharField(verbose_name='上级id', max_length=32, blank=True, null=True)
    model_level = models.IntegerField(choices=model_leval, verbose_name='模块级别', blank=True, null=True)
    model_name = models.CharField(verbose_name='模块名称', max_length=150, blank=True, null=True)
    dev_user = models.CharField(verbose_name='开发负责人', max_length=32, blank=True, null=True)
    test_user = models.CharField(verbose_name='测试负责人', max_length=32, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    update_user = models.CharField(verbose_name='更新人', max_length=32, blank=True, null=True)
    remark = models.CharField(verbose_name='备注', max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        index_together = (('model_level', 'id'), )
        db_table = 'test_app_model'


class TestCase(models.Model):
    # UI测试用例
    id = models.AutoField(primary_key=True)
    test_app_model_id = models.CharField(verbose_name='界面id', max_length=32, blank=True, null=True)
    case_number = models.CharField(verbose_name='用例编号', max_length=150, blank=True, null=True)
    case_name = models.CharField(verbose_name='用例名称', max_length=200, blank=True, null=True)
    case_type = models.CharField(verbose_name='用例类型', max_length=200, blank=True, null=True)
    failed_up = models.IntegerField(verbose_name='后续执行步骤0/1', blank=True, null=True)
    test_file = models.TextField(verbose_name='用例代码', blank=True, null=True)
    update_user = models.CharField(verbose_name='更新人', max_length=32, blank=True, null=True)
    is_common_function = models.IntegerField(verbose_name='是否是公共方法', choices=is_common_function, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    remark = models.CharField(verbose_name='备注', max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ("case_name", )
        db_table = 'test_case'


class TestCaseData(models.Model):
    # UI测试场景步骤数据
    id = models.AutoField(primary_key=True)
    step_desc = models.CharField(verbose_name='步骤描述', max_length=32, blank=True, null=True)
    test_case_id = models.CharField(verbose_name='测试用例id', max_length=32, blank=True, null=True)
    field_desc = models.CharField(verbose_name='字段名', max_length=150, blank=True, null=True)
    location_func = models.CharField(verbose_name='定位方式', max_length=200, blank=True, null=True)
    operate_func = models.CharField(verbose_name='执行方法', max_length=100, blank=True, null=True)
    action_func = models.CharField(verbose_name='步骤方法', max_length=255, blank=True, null=True)
    location_value = models.CharField(verbose_name='定位参数', max_length=1000, blank=True, null=True)
    func_param = models.TextField(verbose_name='执行方法传递参数', blank=True, null=True)
    func_common_param_id = models.IntegerField(verbose_name='执行方法传递参数 公共参数id',  blank=True, null=True)
    mysql_info_id = models.IntegerField(verbose_name='mysql信息 id',  blank=True, null=True)
    ele_attribute = models.CharField(verbose_name='断言 元素属性', max_length=32, blank=True, null=True)
    assert_value = models.CharField(verbose_name='断言 判断值', max_length=200, blank=True, null=True)
    update_user = models.CharField(verbose_name='更新人', max_length=32, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    is_need_value = models.IntegerField(verbose_name='是否需要参数', choices=is_need_value, blank=True, null=True)
    is_need_button = models.IntegerField(verbose_name='是否需要定位', choices=is_need_button, blank=True, null=True)
    is_need_mysql = models.IntegerField(verbose_name='是否是mysql执行方式', choices=is_need_mysql, blank=True, null=True)
    is_need_assert = models.IntegerField(verbose_name='是否需要断言', choices=is_need_assert, blank=True, null=True)
    extension = models.CharField(verbose_name='扩展字段', max_length=255, blank=True, null=True)
    sort = models.IntegerField(verbose_name='执行步骤排序',  blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        index_together = (('test_case_id', ), ('mysql_info_id', ), ('func_common_param_id', ))
        db_table = 'test_case_data'


class UiFunctions(BaseModel):
    # UI测试调用方法存储
    function = models.CharField(verbose_name='执行方法名称', max_length=128, blank=True, null=True)
    is_need_button = models.IntegerField(verbose_name='是否需要定位 0/1', blank=True, null=True)
    is_need_value = models.IntegerField(verbose_name='是否需要传值 0/1', blank=True, null=True)
    function_level = models.IntegerField(verbose_name='方法级别 0/1/2',  blank=True, null=True)
    super_function = models.CharField(verbose_name='上级方法名称', max_length=128, blank=True, null=True)
    description = models.CharField(verbose_name='注释', max_length=128, blank=True, null=True)

    class Meta:
        index_together = (('function', 'function_level'), )
        unique_together = ("function", "super_function")
        db_table = 'ui_functions'


class UiTestScene(models.Model):
    # UI测试场景
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(verbose_name='模块名称', max_length=150, blank=True, null=True)
    fun_name = models.CharField(verbose_name='功能名称', max_length=200, blank=True, null=True)
    scene_name = models.CharField(verbose_name='场景名称', max_length=150, blank=True, null=True)
    scene_desc = models.CharField(verbose_name='场景描述', max_length=225, blank=True, null=True)
    # test_case_ids = models.CharField(verbose_name='测试用例ids', max_length=255, blank=True, null=True)
    update_user = models.CharField(verbose_name='更新人', max_length=32, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    reMark = models.CharField(verbose_name='备注', max_length=225, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'ui_test_scene'


class UiSceneParams(models.Model):
    # UI场景测试数据
    param_dic = models.TextField(verbose_name='参数字典json', blank=True, null=True)
    sort = models.IntegerField(verbose_name='测试数据排序值', blank=True, null=True)
    test_case_index_id = models.IntegerField(verbose_name='场景场景-测试用例中间表id', blank=True, null=True)

    class Meta:
        db_table = 'ui_scene_params'
        index_together = ("test_case_index_id", )


class UiSceneTestCaseIndex(models.Model):
    # UI测试场景下 测试用例排序
    scene_id = models.IntegerField(verbose_name='测试场景id', blank=True, null=True)
    test_case_id = models.IntegerField(verbose_name='测试用例id', blank=True, null=True)
    test_case_index = models.IntegerField(verbose_name='场景下 用例顺序', blank=True, null=True)
    is_need_param = models.IntegerField(verbose_name='此用例是否具有参数 1/0', blank=True, null=True)

    class Meta:
        db_table = 'uiscene_testcase_index'
