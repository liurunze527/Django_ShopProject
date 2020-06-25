from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
#AbstractUser 默认添加了一些用户信息，此处再添加一些符合电商需要的用户信息
class UserProfile(AbstractUser): #后台用户管理继承Django抽象用户,常见属性不用重复写
    """用户信息"""
    GENDER_CHOICES=(
        ('male','男'),
        ('female','女')
    )
    # 用户用手机注册，所以姓名，生日和邮箱可以为空 verbose_name后台admin显示的名称
    name=models.CharField(verbose_name="姓名", max_length=30, null=True, blank=True)#null=True表示数据库存储可以为空, blank=True表示用户提交表单可以为空
    birthday = models.DateField("出生年月", null=True, blank=True)
    gender=models.CharField("性别",max_length=6,choices=GENDER_CHOICES,default='female')
    mobile = models.CharField("电话", max_length=11, null=True, blank=True)
    email = models.EmailField("邮箱", max_length=100, null=True, blank=True)

#数据库元数据操作：后台管理现实的名称（单复数时中文显示相同）
    class Meta:
        verbose_name='用户信息'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.username


#判断手机的验证码和数据库的验证码是否一致
class VerifyCode(models.Model):
    code = models.CharField("验证码", max_length=10)
    mobile = models.CharField("电话", max_length=11)
    add_time = models.DateTimeField("添加时间", default=datetime.now)

    class Meta:
        verbose_name = '短信验证'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code