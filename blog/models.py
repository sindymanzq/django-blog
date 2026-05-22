from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    """文章分类"""

    name = models.CharField("分类名", max_length=50, unique=True)
    # slug 用于 URL 中的英文标识（如 /category/django/）
    slug = models.SlugField("URL 标识", max_length=50, unique=True)

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"

    def __str__(self):
        return self.name


class Post(models.Model):
    """博客文章"""

    # 标题：CharField 用于短文本，max_length 必填
    title = models.CharField("标题", max_length=200)
    # slug：文章在 URL 中的英文标识
    slug = models.SlugField("URL 标识", max_length=200, unique=True)
    # 摘要：TextField 用于长文本，blank=True 表示可选
    summary = models.TextField("摘要", blank=True)
    # 正文：TextField 不限长度
    content = models.TextField("正文")
    # 分类：ForeignKey 一对多关系，一篇文章属于一个分类
    # on_delete=models.CASCADE 表示删除分类时，其下所有文章也一并删除
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="分类",
        related_name="posts",  # 反向查询：category.posts.all()
    )
    # auto_now_add：创建时自动填入当前时间
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    # auto_now：每次保存时自动更新为当前时间
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    # 收藏者：ManyToManyField 自动创建中间表
    favorites = models.ManyToManyField(
        User,
        related_name="favorite_posts",  # 反向查询：user.favorite_posts.all()
        verbose_name="收藏者",
        blank=True,
    )

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        # 默认按创建时间倒序排列
        ordering = ["-created_at"]

    def __str__(self):
        # 在 Admin 后台和 Shell 中显示对象时，显示标题
        return self.title

    # ... 字段定义 ...
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # reverse 根据路由名称和参数反查 URL
        return reverse("post_detail", kwargs={"pk": self.pk})
