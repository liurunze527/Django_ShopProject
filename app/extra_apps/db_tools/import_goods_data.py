# -*- coding: utf-8 -*-


import os
import sys
import django
# pwd = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(pwd + "../")
from app.extra_apps.db_tools.data.product_data import row_data
# 先加载Django配置和Django APP的注册。再导入数据库模型
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ShopProject.settings")
django.setup()
# 先加载Django配置和Django APP的注册。再导入数据库模型
from app.goods.models import Goods, GoodsCategory, GoodsImage


# 依次遍历商品信息
for goods_detail in row_data:
    # 实例化商品对象;
    goods = Goods()
    goods.name = goods_detail["name"]
    # '￥232元'---> 232
    goods.market_price = float(int(goods_detail["market_price"].replace("￥", "").replace("元", "")))
    goods.shop_price = float(int(goods_detail["sale_price"].replace("￥", "").replace("元", "")))
    # 商品描述处理方式
    goods.goods_brief = goods_detail["desc"] if goods_detail["desc"] is not None else ""
    goods.goods_desc = goods_detail["goods_desc"] if goods_detail["goods_desc"] is not None else ""
    # 讲产品轮播图片的第一张图片作为商品列表页显示的图片
    goods.goods_front_image = goods_detail["images"][0] if goods_detail["images"] else ""

    # 商品的三级分类  将商品和商品分类关联。 商品分类只存储的三级分类(可以根据三级分类找到二级分类再找到一级分类)
    category_name = goods_detail["categorys"][-1]  # 获取到三级分类的名称
    category = GoodsCategory.objects.filter(name=category_name)
    if category:
        # 将商品分类对象和商品对象绑定。
        goods.category = category[0]
    goods.save()
    print("添加商品 [%s] 成功" % (goods.name))

    # 添加商品图片
    for goods_image in goods_detail["images"]:
        goods_image_instance = GoodsImage()  # 创建商品轮播图对象
        goods_image_instance.image = goods_image
        goods_image_instance.goods = goods   # 将轮播图对象和商品对象绑定
        goods_image_instance.save()
