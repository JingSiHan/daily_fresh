from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic import View
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse

from apps.user.models import Address
from apps.goods.models import GoodsSKU
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re
from utils.mixin import LoginRequireMixin
from celery_tasks import tasks
from django_redis import get_redis_connection


User = get_user_model()
# Create your views here.

# /user/register
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
        #
        # subject = '天天生鲜欢迎信息'
        # message = ''
        # sender = settings.EMAIL_FROM
        to_email = [email]
        # html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员。</h1>请点击下面的链接激活账户：</br> ' \
        #                '<a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s' \
        #                '</a>' % (user, token, token)

        tasks.send_register_active_eamil(to_email, username, token)

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

            # 激活成功，跳转到登录页面，跳转仍然是反向解析
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            # 激活链接已经过期
            # 应该返回某个链接, 再发一次激活的邮件。
            return HttpResponse('链接已过期，请重新注册。')


# /user/login
class LoginView(View):
    """登录页面"""
    def get(self, request):

        # 判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # 使用模板
        return render(request, 'templates/login.html', {'username': username, 'checked': checked})

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
                # 用户已激活，记录用户的登录状态。session
                login(request, user)
                # 获取登陆后所要跳转到的地址，登录装饰器login_require需求时用到。
                # 默认跳转到首页，url提交的数据使用GET获取，表单采用POST.get()获取
                next_url = request.GET.get('next', reverse('goods:index'))  # 如果有next值，则返回next值，否则返回后面的referse地址
                # 跳转到next_url
                return redirect(next_url)

                response = redirect(reverse('goods:index'))
                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response

            else:
                # 用户未激活
                return render(request, 'templates/login.html', {'errmsg': '账号未激活，请先激活账户。'})  # 应该发激活邮件。
        else:
            # 用户名或密码错误
            return render(request, 'templates/login.html', {'errmsg': '用户名或密码不正确。'})


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        # 使用django内置的用户系统
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))


# /user/info/
class UserInfoView(LoginRequireMixin, View):
    def get(self, request):

        # 获取用户信息
        user = request.user
        address = Address.objects.get_default_address(user=user)

        # 获取用户的历史浏览记录

        # 原本使用redis的方法：
        # from redis import StrictRedis
        # StrictRedis(host='127.0.0.1', port='6379', db=9)
        con = get_redis_connection('default')
        history_key = 'history_%d' %user.id

        # 获取用户最新浏览的5条商品
        sku_ids = con.lrange(history_key, 0, 4)

        # 从数据库中查询用户浏览的商品的具体信息：
        # goods_li = GoodsSKU.objects.filter(goods_id__in=sku_ids)
        # goods_res = []
        # for a_id in goods_li:
        #     for good in goods_li:
        #         if a_id == good:
        #             goods_res.append(good)
        # 遍历获取用户浏览的历史商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文：
        context = {'user': user,
                   'address': address,
                   'goods_li': goods_li,
                   'page': 'info'
                   }

        # 除了认为给template传递变量以外，django会把request.user传给template.即：可以直接在模板文件中使用user.
        return render(request, 'templates/user_center_info.html', context)


# /user/order/
class UserOrderView(LoginRequireMixin, View):
    def get(self, request):
        page = 'order'
        context = {
            'page': page,
        }

        # 获取用户的订单信息
        return render(request, 'templates/user_center_order.html', context)


# /user/address/
class AddressView(LoginRequireMixin, View):
    def get(self, request):
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认地址
        #     address = None
        address = Address.objects.get_default_address(user=user)
        context = {'address': address,
                   'page': 'address'}

        # 获取默认收货地址
        return render(request, 'templates/user_center_site.html', context)

    def post(self, request):
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 数据校验
        if not all([receiver, addr, phone]):
            return render(request, 'templates/user_center_site.html', {'errmsg':'数据不完整。'})
        # 校验手机号
        if not re.match('^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'templates/user_center_site.html', {'errmsg':'手机号码格式不正确。'})

        # 添加地址:如果用户已经添加地址，则新添加的不作为默认地址。如果之前没有地址，那么新添加的作为默认地址。
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认地址
        #     address = None
        address = Address.objects.get_default_address(user=user)
        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 返回应答，刷新地址页面
        return redirect(reverse('user:address'))  # get 请求方式

