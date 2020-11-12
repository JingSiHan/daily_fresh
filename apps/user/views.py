from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic import View
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from utils.mixin import LoginRequireMixin
import re
User = get_user_model()
# Create your views here.

# /user/register


def register(request):
    """注册"""
    if request.method == 'GET':
        # 刚打开网址，注册页面
        return render(request, 'templates/register.html')
    else:
        # 进行注册处理
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验，还可以校验更多信息，此处省略
        # １．是否传完整数据
        if not all((username, password, email)):
            return render(request, 'templates/register.html', {'errmsg': '数据不完整，请完善注册信息。'})

        # 2 判断邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'templates/register.html', {'errmsg': '邮箱格式不合法。'})
        # 校验是否勾选协议
        if allow != 'on':
            return render(request, 'templates/register.html', {'errmsg': '请同意协议。'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'templates/register.html', {'errmsg': '用户名已存在，请重新输入。'})

        # 进行业务处理：用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 返回应答，注册完了用户之后，跳转到首页。
        return redirect(reverse('goods:index'))


def register_handle(request):
    # 进行注册处理
    # 接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')

    # 进行数据校验，还可以校验更多信息，此处省略
    # １．是否传完整数据
    if not all((username, password, email)):
        return render(request, 'templates/register.html', {'errmsg': '数据不完整，请完善注册信息。'})

    # 2 判断邮箱格式是否正确
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'templates/register.html', {'errmsg': '邮箱格式不合法。'})
    # 校验是否勾选协议
    if allow != 'on':
        return render(request, 'templates/register.html', {'errmsg': '请同意协议。'})

    # 校验用户名是否重复
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    if user:
        return render(request, 'templates/register.html', {'errmsg': '用户名已存在，请重新输入。'})

    # 进行业务处理：用户注册
    user = User.objects.create_user(username, email, password)
    user.is_active = 0
    user.save()

    # 返回应答，注册完了用户之后，跳转到首页。
    return redirect(reverse('goods:index'))


class RegisterView(View):
    def get(self, request):
        return render(request, 'templates/register.html')

    def post(self, request):
        # 进行注册处理
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验，还可以校验更多信息，此处省略
        # １．是否传完整数据
        if not all((username, password, email)):
            return render(request, 'templates/register.html', {'errmsg': '数据不完整，请完善注册信息。'})

        # 2 判断邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'templates/register.html', {'errmsg': '邮箱格式不合法。'})
        # 校验是否勾选协议
        if allow != 'on':
            return render(request, 'templates/register.html', {'errmsg': '请同意协议。'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'templates/register.html', {'errmsg': '用户名已存在，请重新输入。'})

        # 进行业务处理：用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送邮件激活，包含激活链接： http://127.0.0.1:8000/user/active/user_id
        # 激活链接中需要包含用户的身份信息，并把信息进行加密。通过It`s dangerous

        # 加密用户的信息，生成激活的token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode('utf-8')

        # 发邮件
        subject = '天天生鲜欢迎信息'
        message = ''
        sender = settings.EMAIL_FROM
        receive = [email]
        html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员。</h1>请点击下面的链接激活账户：</br> ' \
                       '<a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s' \
                       '</a>' % (user, token, token)

        send_mail(subject, message, sender, receive, html_message=html_message)

        # 返回应答，注册完了用户之后，跳转到首页。
        return redirect(reverse('goods:index'))


class ActiveView(View):
    """用户激活"""
    def get(self, request, token):
        # 进行解密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取激活用户的id
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 激活成功，跳转到登录页面
            # 跳转仍然是反向解析
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            # 激活链接已经过期
            # 应该返回某个链接, 再发一次激活的邮件。
            return HttpResponse('链接已过期，请重新注册。')

# /user/login


class LoginView(View):
    """登录页面"""
    def get(self, request):
        return render(request, 'templates/login.html')

    def post(self, request):
        """登录校验"""

        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all((username, password)):
            return render(request, 'templates/login.html', {'errmsg': '数据不完整。'})

        # 业务处理：登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # 记录用户的登录状态。session
                login(request, user)
                # 获取登陆后所要跳转到的地址
                # 默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))

                # 跳转到next_url
                return redirect(next_url)
            else:
                return render(request, 'templates/login.html', {'errmsg': '请先激活账户。'})  # 应该发激活邮件。
        else:
            # 用户名或密码错误
            return render(request, 'templates/login.html', {'errmsg': '用户名或密码不正确。'})

        # 返回应答


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        # 使用django内置的用户系统
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequireMixin, View):
    def get(self, request):
        page = 'info'
        return render(request, 'templates/user_center_info.html', {'page': page})
#/user/order
class UserOrderView(LoginRequireMixin, View):
    def get(self, request):
        page = 'order'
        return render(request, 'templates/user_center_order.html', {'page': page})
# /user/address
class AddressView(LoginRequireMixin, View):
    def get(self, request):
        page = 'address'

        return render(request, 'templates/user_center_site.html', {'page': page})
