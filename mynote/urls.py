"""
URL configuration for note project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import re_path as url,path
from mynote import views
# from mynote.views import CreatOk
from django.views.generic import TemplateView
urlpatterns = [
    url("index/", views.index,name="index"),
    url("about/", TemplateView.as_view(template_name='about.html'), name='about'),
    # 搜尋
    url("search/", TemplateView.as_view(template_name='search.html'),name="search"),
    url("searchanser/", views.searchanser,name="searchanser"),    
    # 登入/登出
    url("login/", views.login,name="login"),
    url("logout/", views.logout,name="logout"),
    # 註冊
    url("register/", views.register,name="register"),
    url("creatok/", TemplateView.as_view(template_name='ok_register.html'), name='creatok'),
    # path("creatok/", CreatOk.as_view(), name='creatok'),
    url("checkemail/", views.checkemail,name="checkemail"),
    # 忘記密碼
    url("forget/", views.forget,name="forget"),
    url("changepsw/", views.changepsw,name="changepsw"),
    url("ok_chpsw/", TemplateView.as_view(template_name='ok_chpsw.html'), name='ok_chpsw'),
    # 更新密碼
    url("oldpswchange/", views.oldpswchange,name="oldpswchange"),
    # 會員區
    url("member/", views.member,name="member"),
    url("memberkeep/", views.memberkeep,name="memberkeep"),
    url("memberdowload/", views.memberdowload,name="memberdowload"),
    url("creation/", views.creation,name="creation"),
    # 資料庫建立與刪除
    url("clear/", views.clear,name="clear"),
    url("creatdatas/", views.creatdatas,name="creatdatas"),
    # 小說下載及收藏
    url("download/", views.download,name="download"),
    url("dowlpage/", views.dowlpage,name="dowlpage"),
    url("keep/", views.keep,name="keep"),
    url("dkep/", views.dkep,name="dkep"),
    # 小說分類區
    url("notelist/", views.notelist,name="notelist"),
    url("allnote/", views.allnotes,name="allnote"),
    url("xuanhuan/", views.xuanhuan,name="xuanhuan"),
    url("yanqing/", views.yanqing,name="yanqing"),
    url("xianxia/", views.xianxia,name="xianxia"),
    url("lishi/", views.lishi,name="lishi"),
    url("wangyou/", views.wangyou,name="wangyou"),
    url("lingyi/", views.lingyi,name="lingyi"),
    url("tongren/", views.tongren,name="tongren"),
    url("erciyuan/", views.erciyuan,name="erciyuan"),
    url("danmei/", views.danmei,name="danmei"),
    url("baihe/", views.baihe,name="baihe"),
    url("japan/", views.japan,name="japan"),
    url("fanatsy/", views.fanatsy,name="fanatsy"),
    url("drama/", views.drama,name="drama"),
    url("herotic/", views.herotic,name="herotic"),
    url("blerotic/", views.blerotic,name="blerotic"),
    url("classicbook/", views.classicbook,name="classicbook"),
    url("suspense/", views.suspense,name="suspense"),
    url("girl/", views.girl,name="girl"),
    url("short/", views.short,name="short"),
    
    # url("basepage/", views.basepage,name="basepage"),

]
