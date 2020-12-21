from django.urls import re_path
# from django.contrib.auth.decorators import login_required
from apps.user import views
from apps.user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView, LogoutView

urlpatterns = [
    # re_path(r'^register$', views.register, name='register'),  # 注册
    # re_path(r'^register_handle$', views.register_handle, name='register_handle'),  # 注册
    re_path(r'^register$', RegisterView.as_view(), name='register'),  # 注册
    re_path(r'^logout$', LogoutView.as_view(), name='logout'),  # 注销登录

    re_path(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 激活账户
    re_path(r'^login$', LoginView.as_view(), name='login'),  # 激活成功，显示登录页面
    re_path(r'^info$', UserInfoView.as_view(), name='info'),  # 用户中心-信息页
    re_path(r'^order$', UserOrderView.as_view(), name='order'),  # 用户中心-订单页
    re_path(r'^address$', AddressView.as_view(), name='address'),  # 用户中心-地址页

]
