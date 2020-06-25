import xadmin
from .models import ShoppingCart, OrderInfo, OrderGoods
# Register your models here.
class ShoppingCartAdmin(object):
    """后台购物车显示栏"""
    list_display=['user','goods','nums',]
class OrderInfoAdmin(object):
    """后台订单显示栏"""
    list_display = ["user", "order_sn", "trade_no", "pay_status", "post_script", "order_mount",
                    "order_mount", "pay_time", "add_time"]

    class OrderGoodsInline(object):
        """订单嵌套订单内的所有购买商品详情"""
        model = OrderGoods
        #除了添加时间其余属性都显示
        exclude = ['add_time', ]
        #额外增加一个表格
        extra = 1
        #表格类型为table
        style = 'tab'

    inlines = [OrderGoodsInline, ]


xadmin.site.register(ShoppingCart, ShoppingCartAdmin)
xadmin.site.register(OrderInfo, OrderInfoAdmin)