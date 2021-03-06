from django.shortcuts import render
from django.views.generic import View
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django.core.cache import cache
from django_redis import get_redis_connection
import os
# Create your views here.

# class Test(object):
#     def __init__(self):
#         self.name = 'abc'
# t = Test()
# t.age = 10
# print(t.age)

# http://127.0.0.1:8000


class IndexView(View):
    """首页"""
    def get(self, request):
        """显示首页"""
        # 先尝试从缓存中获取页面信息
        context = cache.get(':1:index_page_data')
        print(context)
        if context is None:
            print('－－－－设置缓存！！！')
            # 获取商品种类信息
            types = GoodsType.objects.all()

            # 获取首页轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')

            for goods in goods_banners:
                print('goods are:', goods)

            # 获取首页促销活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品展示信息
            for type_name in types:
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type_name, display_type=1).order_by('index')
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type_name, display_type=0).order_by('index')

                # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
                type_name.image_banners = image_banners
                type_name.title_banners = title_banners

            # 需要缓存的数据
            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners,
                       'data': 'This is a message!!'
                       }

            user = request.user
            cart_count = 0
            if user.is_authenticated:
                conn = get_redis_connection('default')
                cart_key = 'cart_%d' % user.id
                cart_count = conn.hlen(cart_key)
            context = context.update(cart_count=cart_count)
            print(context)

            # 设置缓存
            cache.set('index_page_data', context, 3600)
            print('写入缓存成功。')

        # 组织模板上下文
        context = cache.get(':1:index_page_data')
        return render(request, 'templates/index.html', context)
