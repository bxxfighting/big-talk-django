'''
第三节 搜索用户
实际业务中，经常用到的就是查找功能
前面介绍过的查找都是精确的等于，下面说一下范围查找或者模糊查找、以及关联查找
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


# 模糊搜索用户

# 查找所有名称中带有"星"字的用户
# icontains为不区分大小写，contains为区分大小写
query = {
    'name__icontains': '星',
}
UserModel.objects.filter(**query).all()

# 查找所有名称中带有"星"字的用户 并且 年龄大于10岁的用户
## gt大于，gte大于等于，lt小于，lte小于等于
query = {
    'name__icontains': '星',
    'age__gt': 10,
}
UserModel.objects.filter(**query).all()

# 查找所有名称中带有"星"字的用户 或者 年龄大于10岁的用户
from django.db.models import Q
UserModel.objects.filter(Q(name__icontains='星')|Q(age__gt=10)).all()

# 查找所有名称中带有"星"字的用户 或者 年龄大于10岁的用户，但是要排除名字中带"卜"字的用户
from django.db.models import Q
UserModel.objects.filter(Q(name__icontains='星')|Q(age__gt=10)).exclude(name__icontains='卜').all()


# 关联查找
# 假设有一个部门的id为1，现在要查找这个部门下关联的用户名称中带有"星"字的
query = {
    'department_id': 1,
}
DepartmentUserModel.objects.filter(**query).filter(user__name__icontains).all()
# 其实我一般不爱这么查找，我喜欢把它分成两次查询
query = {
    'department_id': 1,
}
user_ids = DepartmentUserModel.objects.filter(**query).values_list('user_id', flat=True).all()
query = {
    'id__in': user_ids,
    'name__icontains': '星',
}
UserModel.objects.filter(**query).all()
