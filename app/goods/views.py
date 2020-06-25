from django.shortcuts import render
#信息查出来转为json格式以HTTPRESPOSE的方式返回到页面
# 访问某个路由，执行某个试图函数，返回某个商品信息到页面
# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from app.goods.filters import GoodsFilter

'''
from rest_framework import generics

from rest_framework.response import Response
from rest_framework.views import APIView

from app.goods.models import Goods
from app.goods.serializers import GoodsSerializer

# 方法一: 基于APIView实现视图类
class GoodsListView(APIView):
    """商品列表"""
    def get(self,request,format=None):
        goods=Goods.objects.all()
        # 使用针对商品序列化的类对获取的所有商品信息进行序列化
        goods_serializer=GoodsSerializer(goods,many=True)
        #以 REST 需要的Response（状态码和轻量数据信息）返回给用户
        return Response(goods_serializer.data)

# 方法二: 基于GenericAPIView实现视图类（GenericAPIView，mixins.ListModelMixin）==（generics.ListAPIView）
# 缺陷：每一次都要编写get方法 很麻烦。 如果可以直接在url绑定视图函数和方法就更加方便了
class GoodsListView(generics.ListAPIView):
    # 指定商品的查询集
    queryset = Goods.objects.all()
    # 指定序列化的方式
    serializer_class = GoodsSerializer

    def get(self, request, *args, **kwargs):
        # 不需要自己编写list方法。
        # mixins.ListModelMixin扩展类实现了获取商品详细信息的代码， 因此直接调用即可。
        return self.list(request, *args, **kwargs)
'''

from rest_framework import mixins, viewsets,filters

from app.goods.models import Goods, GoodsCategory, Banner
from app.goods.serializers import GoodsSerializer, CategorySerializer, BannerSerializer


class GoodsPagination(PageNumberPagination):
    '''
    商品列表自定义分页
    '''
    # 默认每页显示的个数
    page_size = 10
    # 可以动态改变每页显示的个数 # http://xxxx/goods/?page=2&page_size=5
    page_size_query_param = 'page_size'
    # 页码参数
    page_query_param = 'page'  # http://xxxx/goods/?page=1
    # 最多能显示多少页
    max_page_size = 100
#此视图函数可以直接在url中绑定http方法与视图函数、或使用router 默认get方法与list绑定， 无需自己写get方法
#mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet：商品列表页、商品详情页
class GoodsListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页
    """
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    #过滤器后端：过滤、搜索、排序
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # 设置filter的类为我们自定义的类
    filter_class = GoodsFilter
    # 搜索,=name表示精确搜索，也可以使用各种正则表达式


    search_fields = ('=name', 'goods_brief')
    # 排序
    ordering_fields = ('sold_num', 'shop_price')

    # Cache requested url for each user for 2 hours
    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        # self为 model: Goods
        """重写retrieve方法， 查看详情时不仅仅返回商品序列化的信息，还需要修改商品的点击数"""
        #当获取(访问)商品的详细信息一次就对商品的点击数加一，并保存到数据库中，最后详情页面显示的点击数是已经加1后的点击数
        instance = self.get_object()
        # ***************** 增加点击数**************************
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@method_decorator(cache_page(5), name='dispatch')
class CategoryViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    list:商品分类列表数据
    """
    #查询一级分类的信息
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页轮播图
    """
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer



