from django.db import models


PARAMS_POSITION_LIST = ['header', 'path', 'body', 'query']
REQUEST_METHOD = ['get', 'post', 'put', 'delete']
DEPRECATED_LIST = (
    (0, '否'),
    (1, '是'),)


class ApiManage(models.Model):
    id = models.AutoField(primary_key=True)
    path = models.CharField(max_length=200, blank=True, null=True, verbose_name='路由地址')
    tag = models.CharField(max_length=200, blank=True, null=True, verbose_name='所属tag')
    server = models.CharField(max_length=100, blank=True, null=True, verbose_name='所属服务')
    api_desc = models.CharField(max_length=200, blank=True, null=True, verbose_name='api功能注释')
    tag_english_desc = models.CharField(max_length=200, blank=True, null=True, verbose_name='tag英文描述')
    request_method = models.CharField(max_length=30, blank=True, null=True, verbose_name='请求方式')
    param_in = models.CharField(max_length=110, blank=True, null=True, verbose_name='参数所在位置 body/query/path/headers')
    request_params_swagger = models.TextField(default='', blank=True, null=True, verbose_name='请求参数 原生swagger格式')
    request_params_json = models.TextField(default='', blank=True, null=True, verbose_name='请求参数  json格式')
    request_params_ls = models.TextField(default='', blank=True, null=True, verbose_name='请求参数，全部参数数据字典')
    response_params_swagger = models.TextField(default='', blank=True, null=True, verbose_name='返回参数 原生swagger格式')
    response_params_json = models.TextField(default='', blank=True, null=True, verbose_name='返回参数 json格式')
    response_params_ls = models.TextField(default='', blank=True, null=True, verbose_name='返回参数，全部参数数据字典')
    request_table_json = models.TextField(default='', blank=True, null=True, verbose_name='请求参数 json格式(匹配 单接口测试 前端表单数据格式)')
    response_table_json = models.TextField(default='', blank=True, null=True, verbose_name='请求参数 json格式(匹配 单接口测试 前端表单数据格式)')
    deprecated = models.IntegerField(default=0, blank=True, null=True, verbose_name='是否已弃用')
    exception_flag = models.IntegerField(blank=True, null=True, verbose_name='解析是否出现问题')
    exception_log = models.CharField(max_length=200, blank=True, null=True, verbose_name='解析问题原因')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间', null=True)
    has_manual = models.IntegerField(blank=True, null=True, verbose_name='是否手动添加/修改 1/0')

    class Meta:
        db_table = 'api_manage'
        ordering = ['-id']
        unique_together = ('request_method', 'path')
        index_together = ('request_method', 'path')


class Scene(models.Model):
    id = models.AutoField(primary_key=True)
    scene_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='场景名称')
    professional_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='业务名称')
    scene_desc = models.CharField(max_length=200, blank=True, null=True, verbose_name='场景描述')
    status = models.CharField(max_length=200, blank=True, null=True, verbose_name='状态')
    create_by = models.CharField(max_length=200, blank=True, null=True, verbose_name='创建人')
    update_by = models.CharField(max_length=200, blank=True, null=True, verbose_name='更新人')
    need_login = models.IntegerField(blank=True, null=True, verbose_name='场景是否需要登录')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间', null=True,)
    remark = models.CharField(max_length=200, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'scene'
        ordering = ['-id']
        # unique_together = ('scene_name',)


class SceneApiConf(models.Model):
    id = models.AutoField(primary_key=True)
    scene = models.ForeignKey(Scene, default='', verbose_name='场景id', null=True, blank=True, on_delete=models.CASCADE)
    api = models.ForeignKey(ApiManage, default='', verbose_name='管理表接口id', null=True, blank=True, on_delete=models.PROTECT)
    sort = models.IntegerField(verbose_name='场景下接口排序值', blank=False, null=False)
    putin_params_conf = models.TextField(default='', blank=True, null=True, verbose_name='入参类型')
    asset_conf = models.TextField(default='', blank=True, null=True, verbose_name='断言类型')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间',null=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间',null=True)
    remark = models.CharField(max_length=200, blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'scene_api_conf'
        ordering = ['-id']


class ApiParams(models.Model):
    id = models.AutoField(primary_key=True)
    api_conf_id = models.ForeignKey(SceneApiConf, default='', verbose_name='场景id', null=True, blank=True, on_delete=models.CASCADE)
    putin_params_json = models.TextField(default='', blank=True, null=True, verbose_name='请求参数详细json')
    asset_json = models.TextField(default='', blank=True, null=True, verbose_name='断言详细json')
    end_request_json = models.TextField(default='', blank=True, null=True, verbose_name='最终请求参数')
    end_asset_json = models.TextField(default='', blank=True, null=True, verbose_name='最终断言json')
    sort = models.IntegerField(verbose_name='接口下值执行排序值', blank=True, null=True)

    class Meta:
        db_table = 'api_params'
        ordering = ['-id']


class SingleApiParams(models.Model):
    id = models.AutoField(primary_key=True)
    api = models.ForeignKey(ApiManage, default='', verbose_name='', null=True, blank=True, on_delete=models.CASCADE)
    req_table_data = models.TextField(default='', blank=True, null=True, verbose_name='请求参数详细json(前端兼容数据)')
    rep_table_data = models.TextField(default='', blank=True, null=True, verbose_name='断言详细json(前端兼容数据)')
    putin_params_json = models.TextField(default='', blank=True, null=True, verbose_name='请求参数详细json')
    asset_json = models.TextField(default='', blank=True, null=True, verbose_name='断言详细json')
    end_request_json = models.TextField(default='', blank=True, null=True, verbose_name='最终请求参数')
    end_asset_json = models.TextField(default='', blank=True, null=True, verbose_name='最终断言json')
    sort = models.IntegerField(verbose_name='接口下值执行排序值', blank=True, null=True)

    class Meta:
        db_table = 'single_api_params'
        ordering = ['-id']
