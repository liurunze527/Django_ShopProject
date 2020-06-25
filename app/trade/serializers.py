import time

from rest_framework import serializers

from ShopProject.settings import APPID, private_key_path, ali_pub_key_path
from app.goods.models import Goods
from app.goods.serializers import GoodsSerializer
from app.trade.models import ShoppingCart, OrderInfo, OrderGoods
from app.trade.utils import AliPay


#serializers的作用
#1：当用户获取数据信息，吧python对象转换为json字符串
#2：当用户上传信息时，验证用户上传的信息是否合法，如果合法就保存到数据库中



class ShopCartSerializer(serializers.Serializer):
    # 获取当前登录的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    #required=True 表示num必须要填
    nums = serializers.IntegerField(required=True, label="数量", min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于1",
                                        "required": "请选择购买数量"
                                    })
    # 这里是继承Serializer，必须指定queryset对象，如果继承ModelSerializer则不需要指定
    # goods是一个外键，可以通过这方法获取goods object中所有的值
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    """
    1. 如果用户已经将商品添加购物车里面，我们就更新商品的数量.
    2. 如果用户没有将商品添加到购物车里面， 创建一条记录。
    """
    # ModelSerializer的create遇到已经添加的商品会报错
    # 继承的Serializer没有save功能，必须写一个create方法
    def create(self, validated_data):
        # validated_data是已经处理过的数据
        # 获取当前用户
        # view中:self.request.user；serizlizer中:self.context["request"].user
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]
        #在数据库查看商品是否存在在购物车中
        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        # 如果购物车中有记录，数量+1
        # 如果购物车车没有记录，就创建
        if existed:
            existed = existed[0] #数据库中查到当前商品已经添加到购物车中，取出第一条记录
            existed.nums += nums # 再次将当前商品加入购物车直接增加数量
            existed.save() #保存到数据库中
        else:
            # 添加到购物车, **validated_data, 对字典解包。验证的数据以字典存储
            existed = ShoppingCart.objects.create(**validated_data)

        return existed#返回购物车对象

    def update(self, instance, validated_data):
        # 更新商品数量
        instance.nums = validated_data["nums"]
        # 保存到数据库中
        instance.save()
        # 将新的对象返回
        return instance

#显示购物车商品详情的序列化
class ShopCartDetailSerializer(serializers.ModelSerializer):
    '''
    购物车商品详情信息
    '''
    #many=False 一个购物车对应一个商品
    # 此处可以理解为用户要买多个商品，就会有多个购物车，一个购物车id对应一个商品id
    goods = GoodsSerializer(many=False, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ("goods", "nums")

class OrderSerializer(serializers.ModelSerializer):
    """订单序列化  设置read_only的属性不显示在前端之外其余数据库表中所有属性均显示"""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 生成订单的时候这些不用post
    # 订单状态
    pay_status = serializers.CharField(read_only=True)
    # 订单号一定要唯一(unique=True)
    order_sn = serializers.CharField(read_only=True)
    # 支付时间
    pay_time = serializers.DateTimeField(read_only=True)
    # 订单的支付类型
    pay_type = serializers.CharField(read_only=True)
    # 支付宝交易号
    trade_no = serializers.CharField(read_only=True)
    # 微信支付会用到
    nonce_str = serializers.CharField(read_only=True)
    # 订单添加时间是只读的
    add_time = serializers.DateTimeField(read_only=True)
    # 订单的金额是只读的
    order_mount = serializers.FloatField(read_only=True)
    # 支付订单的url
    #创建订单时跳转到支付界面 获取订单以及订单详情时需要一个支付的url地址
    alipay_url = serializers.SerializerMethodField(read_only=True)

#SerializerMethodField会自动去找get_属性名方法去执行来获取属性信息，因此函数名 get_alipay_url的get后必须要与属性名 alipay_url一致
    # get_extra_info(self, obj):源码中给了范例， 必须接收obj对象与self相同
    def get_alipay_url(self, obj):
        # 实例化AliPay的对象
        alipay = AliPay(
            appid=APPID,
            # 支付成功之后通知的url地址， 以post方法发起请求
            # 支付完成后支付宝官方的响应：是否成功，给项目的哪个路由地址响应
            app_notify_url="http://139.129.242.232.:8000/alipay/return/",
            # 应用私钥
            app_private_key_path=private_key_path,
            # 支付宝的公钥
            alipay_public_key_path=ali_pub_key_path,
            debug=True,  # 默认False,
            # 支付成功后返回的url地址， 以get方法发起请求
            # 支付成功后跳转的页面
            return_url="http://139.129.242.232:8000/alipay/return/"
        )
        # 支付信息的完善
        data = alipay.direct_pay(
            subject=obj.order_sn,  # 支付的标题是订单号
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )
        #支付的url地址
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=data)
        return re_url #返回到 alipay_url

    def generate_order_sn(self):
            # 生成订单号
            # 当前时间 + userid + 随机数(2位)
            import random
            # 当前时间，eg: '20200329152308'
            # 按照格式生成相应的时间样式
            now_time = time.strftime("%Y%m%d%H%M%S")
            userid = self.context['request'].user.id
            ranstr = "%.3d" % (random.randint(1, 99)) #"%.3d" % (1)==001
            #{time_str}{userid}{ranstr}为自定义模板，往里面填入值即可
            order_sn = "{time_str}{userid}{ranstr}".format(time_str=now_time, userid=userid, ranstr=ranstr)
            return order_sn
# 用户提交信息后需要先验证数据信息attrs，在验证的过程中自动生成一个订单号添加到序列化数据中 验证后会保存到数据库中
    def validate(self, attrs):
        # validate中添加order_sn，然后在view中就可以save
        attrs["order_sn"] = self.generate_order_sn() #此处调用生成订单号的函数
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"

#OrderGoods：订单商品详情（订单、商品、商品数量、添加事件），一个商品详情对应一个商品，与goods是1对1关系
# OrderGoods的order属性设置了OrderInfo反向引用goods，OrderInfo通过goods属性就可以从订单详情OrderInfo查看订单商品详情OrderGoods
# 订单中的商品
class OrderGoodsSerialzier(serializers.ModelSerializer):
    """ 1个商品详情对应一个商品"""
    #订单商品详情序列化
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods #订单商品类绑定到一起 除了显示商品的详情之外，还需要显示OderGoods的属性
        fields = "__all__"


# 订单商品信息
# goods字段需要嵌套一个OrderGoodsSerializer
class OrderDetailSerializer(serializers.ModelSerializer):
    """many=True一个订单有多个商品，为订单详情添加商品详情"""
    # 此goods是OrderGoods的order属性设置的OrderInfo反向引用goods  OrderInfo.goods就是订单商品对象
    #OrderInfo没有能直接查看商品的属性，但是有外键goods可以实例化OrderGoods类，而OrderGoods.goods可以查找到商品的详情
    #OrderInfo.goods-->OrderGoods()-->OrderGoods.goods
    #因此需要创建一个元数据为 OrderGoods的嵌套商品详情的序列化类
    goods = OrderGoodsSerialzier(many=True) #给订单详情添加商品详情
    # 支付订单的url
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        # 实例化AliPay的对象
        alipay = AliPay(
            appid=APPID,
            # 支付成功之后通知的url地址， 以post方法发起请求
            app_notify_url="http://139.129.242.232.:8000/alipay/return/",
            # 应用私钥
            app_private_key_path=private_key_path,
            # 支付宝的公钥
            alipay_public_key_path=ali_pub_key_path,
            debug=True,  # 默认False,
            # 支付成功后返回的url地址， 以get方法发起请求
            return_url="http://139.129.242.232:8000/alipay/return/"
        )
        # 支付信息的完善
        data = alipay.direct_pay(
            subject=obj.order_sn,  # 支付的标题是订单号
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=data)
        return re_url
    class Meta:
        model = OrderInfo
        fields = "__all__"