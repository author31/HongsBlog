import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from django.db import models
from django.urls import reverse
from django.conf import settings
from uuslug import slugify
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from DjangoBlog.utils import get_current_site
from DjangoBlog.utils import cache_decorator, cache
from django.utils.timezone import now
from mdeditor.fields import MDTextField
from accounts.models import BlogUser
from photologue.models import Gallery

logger = logging.getLogger(__name__)


class LinkShowType(models.TextChoices):
    I = ('i', '首頁')
    L = ('l', '列表頁')
    P = ('p', '文章頁面')
    A = ('a', '全站')
    S = ('s', '友善網站頁面')


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField('新增時間', default=now)
    last_mod_time = models.DateTimeField('修改時間', default=now)

    def save(self, *args, **kwargs):
        if 'slug' in self.__dict__:
            slug = getattr(
                self, 'title') if 'title' in self.__dict__ else getattr(
                self, 'name')
            setattr(self, 'slug', slugify(slug))
        super().save(*args, **kwargs)

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site,
                                            path=self.get_absolute_url())
        return url

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class Article(BaseModel):
    """文章"""
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '發表'),
    )
    TYPE = (
        ('a', '文章'),
        ('p', '頁面'),
    )
    title = models.CharField('標題', max_length=200, unique=True)
    body = MDTextField('內容')
    pub_time = models.DateTimeField(
        '發表時間', blank=False, null=False, default=now)
    status = models.CharField(
        '文章狀態',
        max_length=1,
        choices=STATUS_CHOICES,
        default='p')
    type = models.CharField('類型', max_length=1, choices=TYPE, default='a')
    author = models.ForeignKey(
        BlogUser,
        verbose_name='作者',
        blank=False,
        null=False,
        on_delete=models.CASCADE)
    category = models.ForeignKey(
        'Category',
        verbose_name='分類',
        on_delete=models.CASCADE,
        blank=False,
        null=False)
    gallery = models.ForeignKey(Gallery, blank=True, null=True, verbose_name='相簿', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', verbose_name='標籤集合', blank=True)
    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pub_time']
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_absolute_url(self):
        return reverse('blog:detailbyid', kwargs={
            'article_id': self.id,
            'year': self.created_time.year,
            'month': self.created_time.month,
            'day': self.created_time.day
        })

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))

        return names

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # 下一篇
        return Article.objects.filter(
            id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        # 前一篇
        return Article.objects.filter(id__lt=self.id, status='p').first()


class Category(BaseModel):
    name = models.CharField('分類名稱', max_length=30, unique=True)
    chinese_name = models.CharField('中文名稱', max_length=30, unique=True, null=True)
    parent_category = models.ForeignKey(
        'self',
        verbose_name="上級分類",
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)
    index = models.IntegerField(default=0, verbose_name="權重排序-越大越靠前")

    class Meta:
        ordering = ['-index']
        verbose_name = "分類"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse(
            'blog:category_detail', kwargs={
                'category_name': self.slug})

    def __str__(self):
        return self.name

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        categorys = []

        def parse(category):
            categorys.append(category)
            if category.parent_category:
                parse(category.parent_category)

        parse(self)
        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_sub_categorys(self):
        """
        获得当前分类目录所有子集
        :return:
        """
        categorys = []
        all_categorys = Category.objects.all()

        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                parse(child)

        parse(self)
        return categorys


class Tag(BaseModel):
    """文章标签"""
    name = models.CharField('標籤', max_length=30, unique=True)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_name': self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_article_count(self):
        return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        verbose_name = "標籤"
        verbose_name_plural = verbose_name


class Links(models.Model):

    name = models.CharField('名稱', max_length=30, unique=True)
    link = models.URLField('網址')
    sequence = models.IntegerField('排序', unique=True)
    is_enable = models.BooleanField(
        '是否顯示', default=True, blank=False, null=False)
    show_type = models.CharField(
        '顯示類型',
        max_length=1,
        choices=LinkShowType.choices,
        default=LinkShowType.I)
    created_time = models.DateTimeField('新增時間', default=now)
    last_mod_time = models.DateTimeField('修改時間', default=now)

    class Meta:
        ordering = ['sequence']
        verbose_name = '友善網址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SideBar(models.Model):
    """側邊欄,可以展示一些html内容"""
    name = models.CharField('標題', max_length=100)
    content = models.TextField("内容")
    sequence = models.IntegerField('排序', unique=True)
    is_enable = models.BooleanField('是否啟用', default=True)
    created_time = models.DateTimeField('新增時間', default=now)
    last_mod_time = models.DateTimeField('修改時間', default=now)

    class Meta:
        ordering = ['sequence']
        verbose_name = '側邊欄'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BlogSettings(models.Model):
    '''站点设置 '''
    sitename = models.CharField(
        "網站名稱",
        max_length=200,
        null=False,
        blank=False,
        default='')
    site_description = models.TextField(
        "描述",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    site_seo_description = models.TextField(
        "SEO描述", max_length=1000, null=False, blank=False, default='')
    site_keywords = models.TextField(
        "關鍵字",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    article_sub_length = models.IntegerField("文章摘要長度", default=300)
    sidebar_article_count = models.IntegerField("側邊欄文章数目", default=10)
    show_google_adsense = models.BooleanField('是否顯示廣告', default=False)
    google_adsense_codes = models.TextField(
        '廣告內容', max_length=2000, null=True, blank=True, default='')

    resource_path = models.CharField(
        "静态文件保存地址",
        max_length=300,
        null=False,
        default='/var/www/resource/')

    class Meta:
        verbose_name = '網站配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sitename

    def clean(self):
        if BlogSettings.objects.exclude(id=self.id).count():
            raise ValidationError(_('只能有一個配置'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from DjangoBlog.utils import cache
        cache.clear()


class About(BaseModel):
    title = models.CharField('標題', max_length=200, unique=True, null=True)
    body = MDTextField('內容')
    pub_time = models.DateTimeField(
        '發表時間', blank=False, null=False, default=now)
    class Meta:
        verbose_name = "自我介紹"
        verbose_name_plural = verbose_name


class Page(BaseModel):
    title = models.CharField('標題', max_length=200, unique=True, null=True)
    pub_time = models.DateTimeField('發表時間', blank=False, null=False, default=now)
    gallery = models.ForeignKey(Gallery, blank=True, null=True, verbose_name='相簿', on_delete=models.CASCADE)
    parent_page = models.ForeignKey(
        'self',
        verbose_name="上級分頁",
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    body = MDTextField('內容', null=True, blank=True)
    class Meta:
        verbose_name = "資訊頁面"
        verbose_name_plural = verbose_name  
    
    def __str__(self):
        return self.title

    
    def get_absolute_url(self):
        return reverse(
            'blog:info_page', kwargs={'page_id': self.id})