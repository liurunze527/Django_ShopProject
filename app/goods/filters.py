
#自定义一个过滤器
import django_filters
from django.db.models import Q

from app.goods.models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    '''
    商品过滤的类
    '''
    # 两个参数，name是要过滤的字段，lookup是执行的行为，‘小与等于本店价格’
    price_min = django_filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    # 以商品的分类属性进行过滤，自定义过滤方法
    top_category=django_filters.NumberFilter(field_name='category_id',method='top_category_filter')
    def top_category_filter(self,query_set,name,value):
        """
        
        :param query_set: goods.objects.all()
        :param name: category
        :param value:  id
        :return: 
        """
        #根据一级分类id=传入的value或者 二级与三级分类id
        return Goods.objects.filter(Q(category_id=value)|
                                    Q(category__parent_category_id=value)|
                                    Q(category__parent_category__parent_category_id=value)
                                    )
    class Meta:
        model = Goods
        # http://xxxx/goods/?price_min=10&price_max=100
        fields = ['price_min', 'price_max','is_hot','is_new']