from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q  # Q 对象用于组合复杂查询条件
from .models import Post, Category
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


def register(request):
    """用户注册视图"""
    # 如果用户已登录，直接跳转首页
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        # 用户提交了注册表单
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # 保存用户到数据库
            login(request, user)  # 注册后自动登录
            messages.success(request, f"注册成功，欢迎你，{user.username}！")
            return redirect("index")
    else:
        # GET 请求：显示空白注册表单
        form = RegisterForm()
    return render(
        request, "blog/register.html", {"form": form, "title": "注册 - RUNOOB 博客"}
    )


@login_required
def index(request):
    """博客首页：展示文章列表，支持分类筛选 + 关键词搜索"""
    posts = Post.objects.all().order_by("-created_at")
    # 1. 获取查询参数
    category_slug = request.GET.get("category", "").strip()
    keyword = request.GET.get("q", "").strip()
    # 2. 按分类筛选
    if category_slug:
        # category__slug：通过外键访问分类表的 slug 字段（双下划线）
        posts = posts.filter(category__slug=category_slug)
    # 3. 按关键词搜索（标题或摘要）
    if keyword:
        # Q(title__icontains=...) | Q(summary__icontains=...)：OR 组合
        # icontains：大小写不敏感的包含查询
        posts = posts.filter(
            Q(title__icontains=keyword) | Q(summary__icontains=keyword)
        )
    # 4. 获取所有分类（用于渲染筛选导航）
    categories = Category.objects.all()
    context = {
        "posts": posts,
        "categories": categories,
        "category_slug": category_slug,  # 传给模板，用于高亮当前选中
        "keyword": keyword,  # 回显搜索关键词
        "title": "RUNOOB 博客 - 首页",
    }
    return render(request, "blog/index.html", context)


def post_detail(request, pk):
    """文章详情页"""
    # get_object_or_404：查询单条记录
    # 找到就返回对象，找不到自动返回 404 页面（不写 try/except）
    post = get_object_or_404(Post, pk=pk)
    context = {"post": post, "title": f"{post.title} - RUNOOB 博客"}
    return render(request, "blog/post_detail.html", context)


@login_required
def toggle_favorite(request, pk):
    """切换收藏状态：收藏 → 取消，未收藏 → 收藏"""
    post = get_object_or_404(Post, pk=pk)
    # 检查当前用户是否已收藏
    if post.favorites.filter(id=request.user.id).exists():
        # 已收藏 → 取消收藏
        post.favorites.remove(request.user)
        messages.info(request, f"已取消收藏「{post.title}」")
    else:
        # 未收藏 → 添加收藏
        post.favorites.add(request.user)
        messages.success(request, f"已收藏「{post.title}」")
    # 重定向回当前页面（HTTP_REFERER 是来源页面的 URL）
    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer)


@login_required
def favorites(request):
    """当前用户的收藏列表"""
    # 通过 related_name 反向查询用户的收藏文章
    posts = request.user.favorite_posts.all().order_by("-created_at")
    return render(
        request,
        "blog/favorites.html",
        {"posts": posts, "title": "我的收藏 - RUNOOB 博客"},
    )


class PostListView(LoginRequiredMixin, ListView):
    """博客首页：继承 ListView，展现文章列表"""

    model = Post  # 指定模型
    template_name = "blog/index.html"  # 指定模板（默认：blog/post_list.html）
    context_object_name = "posts"  # 模板中使用的变量名（默认：object_list）
    paginate_by = 12  # 每页 12 条（分页）
    ordering = ["-created_at"]  # 排序

    def get_queryset(self):
        """重写查询方法：支持分类筛选 + 关键词搜索"""
        queryset = super().get_queryset()
        # 分类筛选
        self.category_slug = self.request.GET.get("category", "")
        if self.category_slug:
            queryset = queryset.filter(category__slug=self.category_slug)
        # 关键词搜索
        self.keyword = self.request.GET.get("q", "")
        if self.keyword:
            queryset = queryset.filter(
                Q(title__icontains=self.keyword) | Q(summary__icontains=self.keyword)
            )
        return queryset

    def get_context_data(self, **kwargs):
        """重写上下文方法：往模板中注入额外数据"""
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["category_slug"] = self.category_slug
        context["keyword"] = self.keyword
        context["title"] = "RUNOOB 博客 - 首页"
        return context


class PostDetailView(DetailView):
    """文章详情页：继承 DetailView"""

    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    # pk_url_kwarg：URL 中传递主键的参数名（默认是 pk，这里显式声明一下）
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"{self.object.title} - RUNOOB 博客"
        return context


class FavoriteListView(LoginRequiredMixin, ListView):
    """收藏列表：需要登录才能访问"""

    model = Post
    template_name = "blog/favorites.html"
    context_object_name = "posts"
    ordering = ["-created_at"]

    # LoginRequiredMixin 未登录用户会自动跳转到 settings.LOGIN_URL
    def get_queryset(self):
        # 只显示当前用户收藏的文章
        return self.request.user.favorite_posts.all().order_by("-created_at")
