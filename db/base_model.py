from django.db import models
import datetime


class BaseModel(models.Model):
    """模型抽象基类"""

    create_time = models.DateTimeField(auto_now=True, verbose_name='创建时间', blank=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', blank=True)
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        """说明是一个抽象模型类"""
        abstract = True
