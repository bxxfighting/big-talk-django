'''
第六节 事务
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


# 现在有一个需求是，创建用户，并且关联到某一部门下
# 这种情况要操作两次数据库，一个是创建用户，一个是创建关联关系
# 这样就存在，创建用户成功了，但是创建关联关系失败了(失败原因就可能很多了)
# 但是我们接到的需求是，要么两步都成功，要么就都不创建
from django.db import transaction

@transaction.atomic
def create_user(name, age, department_id):
    data = {
        'name': '星爷',
        'age': 101,
    }
    user_obj = UserModel.objects.create(**data)
    data = {
        'user_id': user_obj.id,
        'department_id': department_id,
    }
    DepartmentUserModel.objects.create(**data)

# 或者
def create_user(name, age, department_id):
    with transaction.atomic():
        data = {
            'name': name,
            'age': age,
        }
        user_obj = UserModel.objects.create(**data)
        data = {
            'user_id': user_obj.id,
            'department_id': department_id,
        }
        DepartmentUserModel.objects.create(**data)
