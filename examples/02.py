'''
第二节 统一管理model
1. 能统一管理的一定要试着统一管理，省得写太多重复代码
前面说所有表都要有那三个字段，那么，就应该弄一个基础model，然后大家继承它
并且一般情况下我们不需要查找到已经删除的数据，为了不每次都要加上is_deleted=False条件
我们替换原objects，在get_queryset中默认增加上is_deleted=False，这样每次查找就默认加了这个条件
但是如果我们有需要查找已经删除的数据的需求，也可以通过src_objects来查找
'''
from abc import abstractmethod
from django.db import models


class BaseManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    '''
    基础model类
    '''
    dt_create = models.DateTimeField('创建时间', auto_now_add=True)
    dt_update = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    objects = BaseManager()
    src_objects = models.Manager()

    class Meta:
        abstract = True


class UserModel(models.Model):
    '''
    用户表
    '''
    name = models.CharField('名称', max_length=128)
    # 年龄范围肯定不会超过SmallIntegerField的最大值
    age = models.SmallIntegerField('年龄')

    class Meta:
        db_table = 'user'


class DepartmentModel(models.Model):
    '''
    部门表
    '''
    name = models.CharField('名称', max_length=128)

    class Meta:
        db_table = 'department'


class DepartmentUserModel(models.Model):
    '''
    部门关联用户
    '''
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name='用户')
    department = models.ForeignKey(DepartmentModel, on_delete=models.CASCADE, verbose_name='部门')

    class Meta:
        db_table = 'department_user'


# 搜索(不包含已经删除的用户)
query = {
    'name': '星哥',
}
user_obj = UserModel.objects.filter(**query).first()

# 搜索(包含已经删除的用户)
query = {
    'name': '星哥',
}
user_obj = UserModel.src_objects.filter(**query).first()
