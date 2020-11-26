from django.contrib import admin
from django.core.cache import cache
from apps.goods.models import GoodsType, IndexPromotionBanner, IndexTypeGoodsBanner, IndexGoodsBanner

# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # 新增或更新表中数据时调用
        super(IndexPromotionBannerAdmin, self).save_model()

        # 发出任务，让celery　worker重新生成首页静态页面
        from celery_tasks.tasks import generate_static_index
        generate_static_index.delay()

        # 清除首页缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        super(IndexPromotionBannerAdmin, self).delete_model()

        # 发出任务，让celery　worker重新生成首页静态页面
        from celery_tasks.tasks import generate_static_index
        generate_static_index.delay()

        # 清除首页缓存
        cache.delete('index_page_data')


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
