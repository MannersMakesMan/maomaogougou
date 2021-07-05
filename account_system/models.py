from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Permission

from utils.basemodels import BaseModel


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


DepartMentLevel = (
    ("0", 'base'),
    ("1", 'level1'),
    ('2', 'level2'),
    ('3', 'level3'),
    ('4', 'level4'),
    ('5', 'level5')
)


class Department(models.Model):
    # 部门列表字段信息
    department_name = models.CharField(max_length=64, verbose_name="部门名称", null=True, blank=True)
    department_code = models.CharField(max_length=64, verbose_name="部门代码", null=True, blank=True)
    super_department_id = models.CharField(max_length=64, verbose_name="上级部门id", null=True, blank=True)
    super_department_name = models.CharField(max_length=64, verbose_name="上级部门名称", null=True, blank=True)
    super_department_code = models.CharField(max_length=64, verbose_name="上级部门代码", null=True, blank=True)
    level = models.CharField(choices=DepartMentLevel, verbose_name="部门级别", max_length=10, default="1")
    remark = models.CharField(max_length=128, verbose_name="备注", null=True, blank=True)

    class Meta:
        db_table = 'Department'
        ordering = ['-id']
        unique_together = ('department_name',)

    def __str__(self):
        return self.department_name


class Position(BaseModel):
    position_name = models.CharField(max_length=128, verbose_name="职位名称", null=True, blank=True)  # 组织名
    position_desc = models.CharField(max_length=128, verbose_name="职务描述", null=True, blank=True)

    class Meta:
        db_table = 'Position'
        # unique_together = ('position_name',)
        ordering = ['-id']

    def __str__(self):
        return self.position_name


class PermissionGroup(BaseModel):
    # 权限组信息表
    permission_group_name = models.CharField(max_length=128, verbose_name="权限组名称", null=True, blank=True)
    permission_group_desc = models.CharField(max_length=128, verbose_name="权限组描述", null=True, blank=True)
    permission_ids = models.TextField(verbose_name="权限资源id列表", null=True, blank=True)
    user_ls = models.TextField(verbose_name="用户列表 无实际意义 兼容序列化器返回字段", default='', null=True, blank=True)

    class Meta:
        db_table = 'Permission_Group'
        # unique_together = ('permission_group_name',)
        ordering = ['-id']


class PermissionViewResources(BaseModel):
    # 权限资源表
    name = models.CharField(max_length=32, verbose_name="权限资源名称", null=True, blank=True)
    path_eng = models.CharField(max_length=128, verbose_name="路由英文名", default='', null=True, blank=True)
    assembly_name = models.CharField(max_length=32, verbose_name="前端组件名称", default='', null=True, blank=True)
    page_identification = models.CharField(max_length=128, verbose_name="前面页面标识", default='', null=True, blank=True)
    super_resource_id = models.CharField(max_length=64, verbose_name="上级资源id", default='', null=True, blank=True)
    sort_num = models.IntegerField(verbose_name="排序值", default=0, null=True, blank=True)
    redirect = models.CharField(max_length=256, verbose_name="重定向", default='', null=True, blank=True)

    class Meta:
        db_table = 'PermissionView_Resources'
        # unique_together = ('name', )
        index_together = ('super_resource_id', )
        ordering = ['-id']


class UserProfile(AbstractUser):
    # 用户列表字段信息
    department = models.ForeignKey(Department, verbose_name='所属部门', null=True, blank=True, max_length=32,
                                   on_delete=models.SET_NULL)
    password = models.CharField(null=True, blank=True, max_length=128, verbose_name="密码")
    Real_name = models.CharField(max_length=30, null=True, blank=True, verbose_name="真实姓名")
    Entry_date = models.DateField(verbose_name='入职日期', null=True, blank=True)
    position = models.ForeignKey(Position, max_length=12, blank=True, null=True, verbose_name="职位", on_delete=models.CASCADE)
    Numberofvisits = models.IntegerField(verbose_name="访问次数", null=True, blank=True, default=0)
    mailbox = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱", default="")
    gender = models.CharField(max_length=6, choices=(("1", u"男"), ("0", "女")), default="", verbose_name="性别")
    Telephone = models.CharField(null=True, blank=True, max_length=32, verbose_name="电话")
    QQ = models.CharField(null=True, blank=True, max_length=32, verbose_name="QQ")
    remark = models.CharField(null=True, blank=True, max_length=64, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    permission_group = models.ForeignKey(PermissionGroup, related_name='user_PermissionGroup', default='', verbose_name='所属权限组', null=True, blank=True, max_length=32,
                                   on_delete=models.SET_NULL)

    class Meta:
        db_table = 'UserProfile'
        ordering = ['-id']
        unique_together = ('username',)

    def __str__(self):
        return self.username

