from django.db import models

# Create your models here.
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class OAuthUser(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='用户',
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    openid = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, verbose_name='學號')
    token = models.CharField(max_length=300, null=True, blank=True)
    type = models.CharField(blank=False, null=False, max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True)
    matedata = models.TextField(null=True, blank=True)
    created_time = models.DateTimeField('新增時間', default=now)
    last_mod_time = models.DateTimeField('修改時間', default=now)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = 'oauth用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']


class OAuthConfig(models.Model):
    TYPE = (
        ('google', 'Google'),
    )
    type = models.CharField('類型', max_length=10, choices=TYPE, default='a')
    appkey = models.CharField(max_length=200, verbose_name='AppKey')
    appsecret = models.CharField(max_length=200, verbose_name='AppSecret')
    callback_url = models.CharField(
        max_length=200,
        verbose_name='回調地址',
        blank=False,
        default='http://www.google.com')
    is_enable = models.BooleanField(
        '是否顯示', default=True, blank=False, null=False)
    created_time = models.DateTimeField('新增時間', default=now)
    last_mod_time = models.DateTimeField('修改時間', default=now)

    def clean(self):
        if OAuthConfig.objects.filter(
                type=self.type).exclude(
                id=self.id).count():
            raise ValidationError(_(self.type + '已经存在'))

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'oauth配置'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
