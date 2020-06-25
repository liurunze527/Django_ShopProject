报错总结：

一：
raise NodeNotFoundError(self.error_message, self.key, origin=self.origin)
django.db.migrations.exceptions.NodeNotFoundError: Migration users.0001_initial dependencies reference nonexistent parent node ('auth', '0011_update_proxy_permissions')
数据库的报错解决：
删除 users.0001_initial .py 只留下migrations包
、db.sqlite3
重新： makemigrations--> migrate


二：
django2.x报错No module named 'django.core.urlresolvers'
原因就是：django2.0 把原来的 django.core.urlresolvers 包 更改为了 django.urls包，所以我们需要把导入的包都修改一下就可以了。
解决方法就是:
from django.urls import reverse

三：
"trying to load '%s': %s" % (entry[1], e) django.template.library.InvalidTemplateLibrary: Invalid template library specified. ImportError raised when trying to load 'crispy_forms.templatetags.crispy_forms_utils': cannot import name 'allow_lazy' from 'django.utils.functional'

原因是 django-crispy-forms版本过低 升级到最新版本就可以解决
我这里出错的django-crispy-forms版本是1.6.1  我升级到1.8.0不再报以上错误

四：
数据库更新没有识别到userapp里面的数据库内容，把migrations文件和sqlite数据库删除之后，
重新输入 makemigrations 但是显示没有检测到No changes detected，migrate后依然没有关于user的数据库表，而且migrations文件也没有显示到项目目录中
 解决方法：
 在每一个app下新建一个migrations，重新执行 makemigrations--> migrate 数据库更新成功
五：
TypeError at /goods/ __str__ returned non-string (type NoneType)
__str返回的是不是字符串，类型是NoneType，python如果没有return的返回值，那么返回值就是None
报错原因：由于user的model的name参数可以为空导致的
解决方式：修改__str__的返回值：return self.username

六：序列化类用的serializer报错create() must be implemented
明明在序列化类中已经重新写了create（）方法但是网页没有找到，因此关闭pycharm重新运行项目，成功解决

七：发送验证码显示报错IP没有权限
云片网把电话对应的IP加入到白名单中

八： 给项目配虚拟环境里的解释器报错：pycharm please specify a different SDK name
原因：有两个*现有*虚拟环境具有相同的名称（即彼此相同;不同于我正在创建的那个）。删除其中一个之后，我就可以创建新的虚拟环境。
在setting里面的解释器选择里面，打开show all：
解决方式：在以下弹出窗口里边，对于重名环境用右边“-”进行删除即可。

九：upload更新代码到服务器中，但是服务器代码一直未更新
原因：在连接云服务器(start SSH session)时没有指定，所以产生一个临时的配置的许多其他名称的服务器，因此在upload时上传的目录也不正确
mapping的目录不对。
解决方式：删除其他名称的服务器，upload指定服务器SCQserver

十： 公网ip:8000 访问项目无法访问
报错原因： 在云服务器中没有设置允许的端口范围8000
解决：添加8000端口到安全组

# 整体项目流程：
一：先创建五个子应用： users、trade等 并在settings注册创建的子应用
2个办法：
1: pycharm先启动manage.py@ShopProject > startapp app/appname
2:进入项目创建的app包目录下：python ../manage.py startapp  appname  （../manage.py表示当前路径的上一级下的manage.py）
二：后台页面设计：
1：用户认证、商品管理、
    自定义用户认证模型UserProfile生效需要在settings设置AUTH_USER_MODEL= 'users.UserProfile'
    数据库模型设计、迁移数据库、后台管理、app子应用配置（名称显示中文）、 子应用init.py中加载配置、
    迁移数据库操作：makemigrations-->sqlmigrate trade 0001_initial
    数据库导入商品信息与图片：
    创建media文件：放入商品的图片；在extra_apps下创建db_tools包，放入商品数据和导入商品信息的文件。
2： xadmin（更友好的后台管理系统、替代django默认后台管理系统）、DjangoUeditor（商品详情页信息：文字、图片、视频 富文本信息）的安装
    进入安装包文件目录下：
    如果有requirements.txt 需要先安装依赖包文件：python install -i https://pypi.douban.com/simple -r requirements.txt
    之后再： python setup install
    最后：settings注册第三方子应用
3：后台管理设置
    url的配置 xadmin
    xadmin对注册的子应用的管理，到每一个应用下的admin.py 下进行xadmin配置
API设计：
setting加入第三方应用restframework，将商品信息序列化：创建一个类去对商品某些属性序列化；
编写url--> views 获取所有商品信息并调用类进行序列化然后把数据返回给用户--> 用户通过url获取到商品信息序列化后的数据

关于Serializer源码剖析的内容，作为参考资料：
https://www.cnblogs.com/wdliu/p/9131500.html

远程主机的代码连接，使得修改本地代码远程主机自动修改代码；
为pycharm配置远程主机的虚拟环境在pycharm运行代码调试就相当于在远程主机上进行调试

最后：项目面试拓展：https://blog.csdn.net/a_blackmoon/article/details/83272764