from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from app.user_operate.models import UserFav, UserLeavingMessage, UserAddress
from app.user_operate.permissions import IsUserOrReadOnly
from app.user_operate.serializers import UserFavSerializer, UserFavDetailSerializer, LeavingMessageSerializers, \
    AddressSerializer


class UserFavViewset(viewsets.GenericViewSet, mixins.ListModelMixin,
                     mixins.CreateModelMixin, mixins.DestroyModelMixin):
    '''
    用户收藏
    '''
    # queryset = UserFav.objects.all()
    # serializer_class = UserFavSerializer
    # permission是用来做权限判断的
    # IsAuthenticated：必须登录用户；IsUserOrReadOnly：必须是当前登录的用户
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # 搜索的字段, 当访问收藏详细信息/删除商品收藏的时候，根据商品id进行操作
    lookup_field = 'goods_id'

# 重新写perform_create方法
    #当用户创建(点击post)提交对商品的收藏时更新收藏商品的收藏数：goods.fav_num += 1
    def perform_create(self, serializer):
        # 对象： UserFav商品收藏的对象   从序列化类 里面的model： UserFav找对象
        # 先获取商品收藏模型对象
        instance = serializer.save()
        # 获取用户商品收藏对象的商品属性
        goods = instance.goods
        # 更新收藏商品的收藏数
        goods.fav_num += 1
        # 商品信息修改后保存到数据库中
        goods.save()

    # 动态选择serializer
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        elif self.action == "create":
            return UserFavSerializer
        return UserFavSerializer

    def get_queryset(self):
        # 只能查看当前登录用户的收藏，不会获取所有用户的收藏
        return UserFav.objects.filter(user=self.request.user)

class LeavingMessageViewset(mixins.ListModelMixin,mixins.DestroyModelMixin,mixins.CreateModelMixin
                            ,viewsets.GenericViewSet):
    """
    list:获取用户留言
    create：添加留言
    delete：删除留言
    """
    #只有登录的用户才可以留言
    permission_classes = (IsAuthenticated,IsUserOrReadOnly)
    serializer_class = LeavingMessageSerializers
    #只能看到自己的留言
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)

class AddressViewset(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        获取收货地址
    create:
        添加收货地址
    update:
        更新收货地址
    delete:
        删除收货地址
    """
    # 判断是否有权限 是否登录
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # 认证方式: token认证和session认证.
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # 序列化类
    serializer_class = AddressSerializer

    # 指定查询集: 登录用户只能查看自己的收获地址
    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)