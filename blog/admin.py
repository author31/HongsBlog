from django.contrib import admin
# Register your models here.
from .models import Article, Category, Tag, Links, SideBar, BlogSettings
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html


class ArticleListFilter(admin.SimpleListFilter):
    title = _("作者")
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        authors = list(set(map(lambda x: x.author, Article.objects.all())))
        for author in authors:
            yield (author.id, _(author.username))

    def queryset(self, request, queryset):
        id = self.value()
        if id:
            return queryset.filter(author__id__exact=id)
        else:
            return queryset


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = '__all__'


def makr_article_publish(modeladmin, request, queryset):
    queryset.update(status='p')


def draft_article(modeladmin, request, queryset):
    queryset.update(status='d')




makr_article_publish.short_description = '發布選中文章'
draft_article.short_description = '選中文章設置為草稿'


class ArticlelAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('body', 'title')
    form = ArticleForm
    list_display = (
        'id',
        'title',
        'link_to_category',
        'created_time',
        'status',
        'type',)
    list_display_links = ('id', 'title')
    list_filter = (ArticleListFilter, 'status', 'type', 'category', 'tags')
    filter_horizontal = ('tags',)
    exclude = ('created_time', 'last_mod_time', 'author')
    view_on_site = True
    actions = [
        makr_article_publish,
        draft_article,]

    def link_to_category(self, obj):
        info = (obj.category._meta.app_label, obj.category._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.category.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.category.name))

    link_to_category.short_description = '分类目录'

    def get_form(self, request, obj, **kwargs):
        form = super(ArticlelAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super(ArticlelAdmin, self).save_model(request, obj, form, change)

    def get_view_on_site_url(self, obj=None):
        if obj:
            url = obj.get_full_url()
            return url
        else:
            from DjangoBlog.utils import get_current_site
            site = get_current_site().domain
            return site


class TagAdmin(admin.ModelAdmin):
    exclude = ('slug', 'last_mod_time', 'created_time')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('chinese_name', 'name', 'parent_category', 'index')
    exclude = ('slug', 'last_mod_time', 'created_time', )


class LinksAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')


class SideBarAdmin(admin.ModelAdmin):
    list_display = ('name', 'content', 'is_enable', 'sequence')
    exclude = ('last_mod_time', 'created_time')


class BlogSettingsAdmin(admin.ModelAdmin):
    pass


class AboutAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'created_time')
    
    list_display_links = ('id', 'title')


class PageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'created_time')
    
    list_display_links = ('title', )