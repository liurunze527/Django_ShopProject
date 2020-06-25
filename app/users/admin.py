

# Register your models here.
# 后台管理站点注册数据库模型，进行管理


import xadmin
from xadmin import views

from .models import VerifyCode


class BaseSetting(object):
    """xadmin的基本配置"""
    # 开启主题切换功能
    enable_themes = True
    # 支持切换主题
    use_bootswatch = True


class GlobalSettings(object):
    """xadmin的全局配置"""
    # 设置站点标题
    site_title = "SCQ电商平台"
    # 设置站点的页脚
    site_footer = "https://gitee.com/scq1109"
    # 设置菜单折叠，在左侧，默认的
    menu_style = "accordion"


class VerifyCodeAdmin(object):
    # 列表展示的字段
    list_display = ['code', 'mobile', "add_time"]


xadmin.site.register(VerifyCode, VerifyCodeAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting) #后台展示视图函数与我们自定义配置绑定到一起来生效 Django xadmin文档可以查询
xadmin.site.register(views.CommAdminView, GlobalSettings)