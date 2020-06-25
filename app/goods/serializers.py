
#将商品的一些属性序列化 转为字符串
#serializers.Serializer 需要手动输入需要序列化的字段
# from  rest_framework import  serializers
# class GoodsSerializer(serializers.Serializer):
#     name=serializers.CharField(required=True,max_length=100)
#     click_num=serializers.CharField(default=0)
#     goods_front_image=serializers.ImageField()

from rest_framework import serializers
#serializers.ModelSerializer 可以对字段全部序列化
from app.goods.models import Goods, GoodsCategory, GoodsImage, Banner


#先序列化分类表中的字段属性
class CategorySerializer3(serializers.ModelSerializer):
    """3级分类序列化"""
    #子分类为3级分类
    class Meta:
        model = GoodsCategory
        fields='__all__'


class CategorySerializer2(serializers.ModelSerializer):
    """2级分类序列化"""
    #子分类为3级分类
    sub_cat = CategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields='__all__'

#先序列化分类表中的字段属性
class CategorySerializer(serializers.ModelSerializer):
    """一级分类序列化"""
    #子分类为2级分类 (many=True) 属性有多个 且是外键关联其他类需要加入
    sub_cat = CategorySerializer2(many=True)
    class Meta:
        model = GoodsCategory
        fields='__all__'
#轮播图：一个商品对应多个轮播图
class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoodsImage
        fields=('image',) #只对GoodsImage的image属性序列化

#将序列化分类表中的字段属性嵌套入商品信息中
class GoodsSerializer(serializers.ModelSerializer):
    #覆盖外键字段，不指定时，只显示商品的分类属性的id，指定后会将商品的分类属性所在的分类表中的字段属性显示出来
    #将商品的外键：分类category，这个表的信息也序列化并嵌套显示在商品信息下
    category=CategorySerializer() #此处的category必须与商品的分类属性category字段相同，才能对应显示分类的字段属性
    images=GoodsImageSerializer(many=True) #让所有商品嵌套显示goods的images属性所属表GoodsImage的image属性显示出来，即所有轮播图 many=True :一个商品对应多个轮播图
    class Meta:
        model =  Goods #对那个数据库表的属性进行序列化
        fields='__all__' #序列化字段的范围
        #exclude=['goods_desc'] #不显示字段属性、其余字段显示

class BannerSerializer(serializers.ModelSerializer):
    '''
    轮播图
    '''
    class Meta:
        model = Banner
        fields = "__all__"