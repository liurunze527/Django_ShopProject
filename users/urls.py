from django.urls import re_path
from . import views

from django.urls import re_path
from . import views


app_name = 'users'
urlpatterns = [
    re_path(r'index/', views.register, name='index'),
    re_path(r'login/', views.login, name='login'),
    re_path(r'register/', views.register, name='register'),
    re_path(r'user/(?P<pk>\d+)/profile/', views.profile, name='profile'),
    re_path(r'user/(?P<pk>\d+)/profile_update/', views.profile_update, name='profile_update'),
    re_path(r'user/(?P<pk>\d+)/pwd_change/', views.pwd_change, name='pwd_change'),
    re_path(r'logout/', views.logout, name='logout'),
    ]

