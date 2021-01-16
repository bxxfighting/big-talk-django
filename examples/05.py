'''
第四节 按日期聚合
在业务中经常用到根据日期聚合
比如哪一天的数据，哪个月的数据
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


# 按日期聚合
# 统计所有天，每天创建了多少用户
# 在用户model中dt_create为精确到秒(或者毫秒)的时间，但是现在需要聚合到天
from django.db import connection
from django.db.models import Count
select = {'day': connection.ops.date_trunc_sql('day', 'dt_create')}
UserModel.objects.extra(select=select).values('day').annotate(count=Count('id'))
# connection.ops.date_trunc_sql('day', 'dt_create')这就是把原来的数据截断到天
# select = {'day': ....} 这里的day就是自己随意取的名了

# 统计所有月，每月创建了多少用户
select = {'month': connection.ops.date_trunc_sql('month', 'dt_create')}
UserModel.objects.extra(select=select).values('month').annotate(count=Count('id'))
# connection.ops.date_trunc_sql('month', 'dt_create')这就是把原来的数据截断到月
# select = {'month': ....} 这里的month就是自己随意取的名了

# 现在又有一个问题，如果我们数据库中存的时间是UTC时间，那么是差了8个小时的
# 这时候就需要先把8小时加回来，再处理
select = {'day': connection.ops.date_trunc_sql('day', 'DATE_ADD(dt_create, interval 8 hour)')}
UserModel.objects.extra(select=select).values('day').annotate(count=Count('id'))
