from django.forms import ModelForm,  TextInput, URLInput, ClearableFileInput
from .models import Restaurant, Dish


class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        exclude = ('user', 'date',)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'address': TextInput(attrs={'class': 'form-control'}),
            'telephone': TextInput(attrs={'class': 'form-control'}),
            'url': URLInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'name': '名称',
            'address': '地址',
            'telephone': '电话',
            'url': '网站',
        }


class DishForm(ModelForm):
    class Meta:
        model = Dish
        exclude = ('user', 'date', 'restaurant',)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(attrs={'class': 'form-control'}),
            'price': TextInput(attrs={'class': 'form-control'}),
            'image': ClearableFileInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'name': '菜名',
            'description': '描述',
            'price': '价格(元)',
            'image': '图片',
        }

