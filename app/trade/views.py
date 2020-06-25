from datetime import datetime

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ShopProject.settings import APPID, private_key_path, ali_pub_key_path
from app.trade.models import ShoppingCart, OrderInfo, OrderGoods
from app.trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from app.trade.utils import AliPay
from app.user_operate.permissions import IsUserOrReadOnly


class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create：
        加入购物车
    delete：
        删除购物记录
    """
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    serializer_class = ShopCartSerializer
    # 进入详情页更新时查询的关键字 根据商品id去查询购物车中的商品
    lookup_field = "goods_id"

    def perform_create(self, serializer):
        """重写perform_create方法，商品加入购物车时， 存储购物车的商品数量信息，还要更新商品的库存信息 最后再保存"""
        # serializer.save存储的是购物车的数据库模型对象
        # 数据库中的购物车是一个商品对应一个购物车对象，如果添加商品到多个购物车中，更新库存量和购物车商品数量是同时更新所有的购物车对象。
        shopcarts = serializer.save()
        # 获取当前购物车的商品对象.
        goods = shopcarts.goods
        # 商品库存量-购物车商品数量=当前商品库存量
        goods.goods_num -= shopcarts.nums
        goods.save()  #存储购物车的商品信息

    def perform_destroy(self, instance):
        """当删除购物车的时候商品库存量的更新"""
        # serializer.save存储的是购物车的数据库模型对象  商品名称  - 10 +
        shopcarts = instance
        # 获取当前购物车的商品对象.
        goods = shopcarts.goods
        # 购物车里面商品删除， 增加商品的库存量
        goods.goods_num += shopcarts.nums
        # 一定要将更改的信息存储到数据库中.
        goods.save()
        # 将购物车对象删除.
        instance.delete()

    def perform_update(self, serializer):
        """
        当购物车商品数量更新时， 更新商品的库存量(可能增加也可能减少)
            1. 先获取购物车之前商品的数量.    10
            2. 获取购物车现在商品的数量.      9
            3. 发现购物车数量减少1  update_nums = 现在的购物车数量-原先的购物车数量   -1
            4. 100 更新商品库存量加1     100 - (-1) = 101
        """
        # get方法返回的是符合条件的对象， filter返回的是符合条件的列表信息。
        #在数据库中先根据购物车的id获取购物车里面的商品数量
        old_shopcart_nums = ShoppingCart.objects.get(id=serializer.instance.id).nums  # 10
        #获取当前购物车对象(更新购物车商品数量后的购物车对象)
        shopcart = serializer.save()
        #获取当前购物车对象的商品数量
        new_shopcart_nums = shopcart.nums     # 9
        # 计算更新量
        update_nums = new_shopcart_nums - old_shopcart_nums  # -1
        #获取购物车的商品对象
        goods = shopcart.goods  # 库存量100
        #更新商品库存量
        goods.goods_num -= update_nums  # 库存量100-(-1) = 101
        #将更新后的商品库存量保存到数据库中
        goods.save()

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)
    # 动态修改序列化
    # 如果是list就显示购物车所有商品的所有详情信息，如果是在购物车添加商品、查看商品、删除商品只显示商品id和商品数量
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

class OrderViewset(viewsets.ModelViewSet):
    """
    订单管理
    list:
        获取个人订单
    delete:
        删除订单
    create：
        新增订单
    """
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # serializer_class = OrderSerializer

    # 获取订单列表
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    # 动态配置serializer
    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer  #返回包含有商品详情的订单，其余订单详情是OrderSerializer写好后存入数据库在OrderDetailSerializer显示的字段
        return OrderSerializer

    # 在订单提交保存之前还需要多两步步骤，所以这里自定义perform_create方法
    # 1.将购物车中的商品保存到OrderGoods中
    # 2.清空购物车
    def perform_create(self, serializer):
        """序列化验证通过后，执行的内容，默认只是保存序列化的数据， 但此处需要进一步处理"""
        order = serializer.save() #把这些用户填入的订单信息全部保存到数据库中 订单金额不是有用户去填写保存，由系统计算好存入数据库
        # 计算订单里面所有商品的总金额: 单价*数量
        sum_money = 0
        # 获取购物车所有商品
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
    #遍历购物车的商品，每一个商品都存入一次订单商品详情表中
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()
            # 一个商品的金额: 单价*数量
            order_goods_money = order_goods.goods.shop_price * order_goods.goods_num
            sum_money += order_goods_money
            # 清空购物车
            shop_cart.delete()

        order.order_mount = sum_money
        order.save() #此处将订单中的价格保存到数据库中
        return order

class AlipayView(APIView):
    """
        如果支付成功，访问notify_url="http://139.129.242.232:8000/alipay/return/"，此时为视图函数的post方法用于
    确保支付宝官方、获取订单状态、订单号、支付宝交易流水号；订单状态、货品销售量的更新；
        之后再访问return_url="http://139.129.242.232:8000/alipay/return/" 跳转到这个页面此时为get方法 ，返回商家界面success
    以上逻辑全部在实例化alipay对象时传递的参数后类自行执行，也就是支付宝API接口让传入的参数， 我们只要传入参数就可以了;
        支付宝判断用户是否支付成功：用户点击支付链接、支付过程是否成功，成功返回一个trade_success的响应，我们再更新到数据库中，查看支付宝官方API文档可得知。
    再加上我们刚好把数据库支付成功的状态信息设置为trade_success与支付宝返回的支付成功的订单状态信息是一致的，所以才对应起来的。
    """

    def get(self, request):
        """
        支付成功后跳转的页面，不提交任何信息验证后直接跳转页面
        处理支付宝的re_url返回  支付的url地址
        # http://api.alipay.com/gateway?appid=xxx&total_amount=xxx
        request.url
        request.method
        request.GET  {'appid':'xxxx', 'total_amount': 'xxxx'}
        """
        # 处理的字典信息
        processed_dict = {}
        # 1. 获取GET中参数
        for key, value in request.GET.items():
            processed_dict[key] = value
        # 2. pop出做过认证的信息sign
        sign = processed_dict.pop("sign", None)
        # 3. 生成ALipay对象 服务器端生成的支付宝Alipay对象与客服端相互验证，保证安全，防止客服端是黑客
       #与本地私钥、公钥信息进行对比，
        alipay = AliPay(
            appid=APPID,
            app_notify_url="http://139.129.242.232:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,  # 默认False,
            return_url="http://139.129.242.232:8000/alipay/return/"
        )
        #服务端支付宝验证客户端提交的信息、标签
        #确保用户私钥公钥和支付宝官方是认证通过的，避免黑客返回伪造支付成功的消息
        verify_re = alipay.verify(processed_dict, sign)
        return Response('success')

# 用户支付完成后支付宝官方的响应：是否成功，给项目的哪个路由地址响应    post完之后使用get
    def post(self, request):
        """
        处理支付宝的notify_url：支付成功后支付宝官方通知url去提交一些信息，

        """
        # 存放post里面所有的数据
        processed_dict = {}
        # 取出post里面的数据
        for key, value in request.POST.items():
            processed_dict[key] = value
        # 把sign pop掉，文档有说明
        sign = processed_dict.pop("sign", None)

        # 3. 生成ALipay对象
        alipay = AliPay(
            appid=APPID,
            app_notify_url="http://139.129.242.232:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,  # 默认False,
            return_url="http://139.129.242.232:8000/alipay/return/"
        )
        # 进行验证
        verify_re = alipay.verify(processed_dict, sign)

        # 如果验签成功
        if verify_re is True:
            # 商户网站唯一订单号
            order_sn = processed_dict.get('out_trade_no', None)
            # 支付宝系统交易流水号
            trade_no = processed_dict.get('trade_no', None)
            # 交易状态
            trade_status = processed_dict.get('trade_status', None)


#销售量的更新：根据订单号找到当前订单，获取订单的所有商品信息对象，遍历所有商品信息对象，获取商品信息对象的商品属性进而修改销售量最后保存到数据库中。
            # 查询数据库中订单记录 filter返回的是一个列表因此需要遍历existed_orders，通过get获取已经存在的订单返回订单对象本身不需要for循环遍历订单对象
            #事实上，提交的订单也只有一个 遍历只是获取filter返回的列表里面的内容
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                # 遍历订单列表（只有一个订单）， 获取该订单里面所有的商品信息对象集合order_goods,
                # 订单里面的商品信息order_goods是OrderGoods实例化的对象:  <QuerySet [<OrderGoods: 202004050120512076>, <OrderGoods: 202004050120512076>]>
                order_goods = existed_order.goods.all() #OrderInfo类实例化对象通过反向引用的goods属性是OrderGoods实例化的对象，有很多商品因此存储到列表中
                # print("订单里面的商品信息: ", order_goods)
                # 订单支付成功，商品的销售量也对应增加。
                for ordergood in order_goods:#遍历所有商品的商品信息
                    # 获取OrderGoods实例化的对象ordergood的商品属性
                    good = ordergood.goods
                    # print("商品名称: %s 当前销量 %s" % (good.name, good.sold_num))
                    good.sold_num += ordergood.goods_num  # 商品销量 = 商品销量 + 订单里面的商品数量
                    # print("商品名称: %s 当前销量 %s" % (good.name, good.sold_num))
                    good.save()
                # 更新订单状态
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()
            # 需要返回一个'success'给支付宝，如果不返回，支付宝会一直发送订单支付成功的消息
            return Response("success")