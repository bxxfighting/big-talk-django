'''
第一节 创建model
一个用户model，一个部门model，一个关联model
1. 这个关联model其实可以使用django的ManyToManyField，但是我想自己掌控关联表
2. 所有表都应该有dt_create dt_update is_deleted字段(我是这么认为的)
   不要实际删除数据，所有删除都通过is_deleted=True为代表，平时筛选时增加is_deleted=False
3. 所有表都应该指定db_table，不要使用默认生成的表名？不丑？
4. 所有字段都设置上verbose_name字段，
   外键的时候需要显示的指定，其它字段都是第一个参数就是，不需要显示指定
'''
from django.db import models


class UserModel(models.Model):
    '''
    用户表
    '''
    name = models.CharField('名称', max_length=128)
    # 年龄范围肯定不会超过SmallIntegerField的最大值
    age = models.SmallIntegerField('年龄')
    # 创建时自动设置成创建时的时间
    dt_create = models.DateTimeField('创建时间', auto_now_add=True)
    # 创建时自动设置成创建时的时间，使用save更新时，自动设置成更新时的时间
    dt_update = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        db_table = 'user'


class DepartmentModel(models.Model):
    '''
    部门表
    '''
    name = models.CharField('名称', max_length=128)
    dt_create = models.DateTimeField('创建时间', auto_now_add=True)
    dt_update = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        db_table = 'department'


class DepartmentUserModel(models.Model):
    '''
    部门关联用户
    我的建议是，即使在你拿到需求的时候，觉得一对多就可以满足了，我还是建议按多对多处理
    因为多对多可以在程序上写成一对多，但是一对多却不支持多对多(产品经理的话不要轻信)
    '''
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name='用户')
    department = models.ForeignKey(DepartmentModel, on_delete=models.CASCADE, verbose_name='部门')
    dt_create = models.DateTimeField('创建时间', auto_now_add=True)
    dt_update = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)

    class Meta:
        db_table = 'department_user'


# 创建用户
data = {
    'name': '卜星星',
    'age': 100,
}
UserModel.objects.create(**data)

# 查找用户
# 我们这里是假设用户名称不允许重复的情况下，通过name查找用户，后面用first，因为最多就一个用户，或者没有
# 当没有时，返回为None
query = {
    'name': '卜星星',
    'is_deleted': False,
}
user_obj = UserModel.objects.filter(**query).first()

# 批量创建用户
data_list = [
    { 'name': '张三', 'age': 101, },
    { 'name': '李四', 'age': 121, },
]
obj_list = []
for data in data_list:
    obj_list.append(UserModel(**data))
UserModel.objects.bulk_create(obj_list)

# 更新用户: update
data = {
    'name': '星爷',
}
query = {
    'name': '卜星星',
    'is_deleted': False,
}
UserModel.objects.filter(**query).update(**data)

# 更新用户: save
query = {
    'name': '星爷',
    'is_deleted': False,
}
user_obj = UserModel.objects.filter(**query).first()
if user_obj:
    user_obj.name = '星哥'
    user_obj.save()
# 在使用save更新时，dt_update字段时间会自动更新，但是update却不会更新这个字段
