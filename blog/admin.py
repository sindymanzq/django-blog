from django.contrib import admin
from .models import Category, Post
from django_summernote.admin import SummernoteModelAdmin


# 注册分类模型：最简单的注册方式
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 列表页显示的列
    list_display = ["name", "slug"]


# 注册文章模型：带自定义配置
# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     # 列表页显示的列
#     list_display = ["title", "category", "created_at", "updated_at"]
#     # 右侧过滤栏：按分类和时间过滤
#     list_filter = ["category", "created_at"]
#     # 顶部搜索框：按标题和摘要搜索
#     search_fields = ["title", "summary"]
#     # 发布时间的层级导航（年 → 月 → 日）
#     date_hierarchy = "created_at"
#     # 每页显示 20 条记录
#     list_per_page = 20


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):  # 继承 SummernoteModelAdmin
    list_display = ["title", "category", "created_at"]
    list_filter = ["category"]
    search_fields = ["title", "summary"]
    summernote_fields = ["content"]  # content 字段使用富文本编辑器
