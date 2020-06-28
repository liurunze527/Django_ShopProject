from django.urls import path, re_path
from . import views

# namespace
app_name = 'myrestaurants'
urlpatterns = [
# 查看餐厅列表
    path('', views.RestaurantList.as_view(), name='restaurant_list'),

# 查看餐厅详情, 如/myrestaurants/restaurant/1/
    re_path(r'^restaurant/(?P<pk>\d+)/$',
        views.RestaurantDetail.as_view(), name='restaurant_detail'),

# 创建餐厅, 如：/myrestaurants/restaurant/create/
    re_path(r'^restaurant/create/$', views.RestaurantCreate.as_view(), name='restaurant_create'),

# 编辑餐厅详情, 如: /myrestaurants/restaurant/1/edit/
    re_path(r'^restaurant/(?P<pk>\d+)/edit/$',
        views.RestaurantEdit.as_view(), name='restaurant_edit'),
# 创建菜品 ex.: /myrestaurants/restaurant/1/dishes/create/
    re_path(r'^restaurant/(?P<pk>\d+)/dishes/create/$',
            views.DishCreate.as_view(), name='dish_create'),

# 编辑菜品, ex.: /myrestaurants/restaurant/1/dishes/1/edit/
    re_path(r'^restaurant/(?P<pkr>\d+)/dishes/(?P<pk>\d+)/edit/$',
            views.DishEdit.as_view(), name='dish_edit'),

# 查看菜品信息 ex: /myrestaurants/restaurants/1/dishes/1/
    re_path(r'^restaurant/(?P<pkr>\d+)/dishes/(?P<pk>\d+)/$',
            views.DishDetail.as_view(), name='dish_detail'),

# 创建餐厅评论, /myrestaurants/restaurant/1/reviews/create/
    re_path(r'^restaurant/(?P<pk>\d+)/reviews/create/$',
            views.review_create, name='review_create'),

]