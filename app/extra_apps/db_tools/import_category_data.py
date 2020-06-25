# -*- coding: utf-8 -*-


#独立使用django的model
import sys
import os


#导入django配置文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ShopProject.settings")

import django
django.setup()


from app.goods.models import GoodsCategory
from app.extra_apps.db_tools.data.category_data import row_data

#遍历一级类目
for lev1_cat in row_data:
    lev1_intance = GoodsCategory()
    lev1_intance.code = lev1_cat["code"]
    lev1_intance.name = lev1_cat["name"]
    lev1_intance.category_type = 1
    lev1_intance.save()
    print("添加一级分类 [%s] 成功" %(lev1_intance.name))
#遍历二级类目
    for lev2_cat in lev1_cat["sub_categorys"]: #lev1_cat是一个字典，字典key为sub_categorys，对应value为二级类目
        lev2_intance = GoodsCategory()
        lev2_intance.code = lev2_cat["code"]
        lev2_intance.name = lev2_cat["name"]
        lev2_intance.category_type = 2
        #指定父级类目为lev1_intance
        lev2_intance.parent_category = lev1_intance
        lev2_intance.save()
        print("  --添加二级分类 [%s] 成功" %(lev2_intance.name))

        for lev3_cat in lev2_cat["sub_categorys"]:
            lev3_intance = GoodsCategory()
            lev3_intance.code = lev3_cat["code"]
            lev3_intance.name = lev3_cat["name"]
            lev3_intance.category_type = 3
            lev3_intance.parent_category = lev2_intance
            lev3_intance.save()
            print("    ----添加三级分类 [%s] 成功" % (lev3_intance.name))

