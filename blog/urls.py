from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# 应用路由表
urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("register/", views.register, name="register"),
    # Django 内置登录视图
    # template_name：指定使用哪个模板
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="blog/login.html",
            redirect_authenticated_user=True,  # 已登录用户访问 login 直接跳转
        ),
        name="login",
    ),
    # Django内置登出视图，标准写法
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="login"  # 直接写路由名，登出跳首页index，比写/更规范
        ),
        name="logout",
    ),
]
