from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
from celery import Celery
import os
import time

# 在worker端使用以下代码
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily_fresh.settings')
django.setup()
# 在worker端使用以上代码，否则以下几个类找不到

from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner


# 0用于练习，１用于保存cession，２用作broker
app = Celery('celery_tasks.tasks', broker='redis://192.168.1.19:6379/2')


# 定义任务函数
@app.task
def send_register_active_eamil(to_email, username, token):
    # 发邮件
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receive = [to_email]
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员。</h1>请点击下面的链接激活账户：</br> ' \
                   '<a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s' \
                   '</a>' % (username, token, token)

    send_mail(subject, message, sender, receive, html_message=html_message)
    time.sleep(5)


@app.task
def generate_static_index():
    # 获取商品种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')  # 待确认
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模板上下文
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 使用模板
    # 使用模板，返回模板对象
    temp = loader.get_template('templates/static_index.html')

    # 渲染模板文件
    static_index_html = temp.render(context)

    # 生成首页对应的静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')

    with open(save_path, 'w') as f:
        f.write(static_index_html)
