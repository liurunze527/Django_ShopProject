import json

from django.core import serializers
from django.http import JsonResponse
from django.views import View

from app.goods.models import Goods

class GoodsListSerializerView(View): #通过django的view实现商品列表页
    def get(self,request ):
        json_list=[]
        goods=Goods.objects.all()  #获取所有商品
        json_data=serializers.serialize('json',goods) #将商品信息全部转为json
        json_data=json.loads(json_data)#json改为python格式
        return JsonResponse(json_data,safe=False) #In order to allow non-dict objects to be serialized set the safe parameter to False.