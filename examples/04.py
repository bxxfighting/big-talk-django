'''
第四节 聚合
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


# 最简单的聚合
# 一共有多少用户
UserModel.objects.count()
# 一共有多少名称带"星"字的用户
query = {
    'name__icontains': '星',
}
UserModel.objects.filter(**query).count()

# 所有带"星"字用户年龄之和
from django.db.models import Sum
query = {
    'name__icontains': '星',
}
UserModel.objects.filter(**query).aggregate(total=Sum('age')).get('total') or 0
# 所有符合条件的用户年龄相加，赋值给一个新的key叫total，然后取total的值即可

# 每个部门都有多少用户
# 这里使用的是分组聚合
from django.db.models import Count
# 这里使用values，返回值是一个字典的列表
results = DepartmentUserModel.objects.values('department_id').annotate(total=Count('user_id'))
for r in results:
    department_id = r.get('department_id')
    total = r.get('total')

# 这里使用values_list，返回值是一个元组的列表
results = DepartmentUserModel.objects.values_list('department_id').annotate(total=Count('user_id'))
for r in results:
    department_id, total = r

# 这里可以提一下values和values_list的区别
# values和values_list都是指定返回的字段，但是values是以key: value的形式返回字典列表
# 而values_list是以元组的形式返回元组列表，并且当values_list中只指定一个字段时，可以增加flat=True，这样就返回单纯的列表
# 示例

UserModel.objects.values('id', 'age').all()
# 返回的是[{'id': 1, 'age': 100}, {'id': 2, 'age': 121}]

UserModel.objects.values_list('id', 'age').all()
# 返回的是[(1, 100), (2, 121)]

UserModel.objects.values_list('id').all()
# 返回的是[(1,), (2,)]

UserModel.objects.values_list('id', flat=True).all()
# 返回的是[1, 2]
