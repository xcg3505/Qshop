from django.urls import path,re_path
from Seller.views import *
urlpatterns=[
    re_path('^$',index),
    path('index/',index),
    path('login/',login),
    path('logout/',logout),
    path('gad/',goods_add),
    path('glt/',goods_list),

]
