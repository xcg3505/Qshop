from django.shortcuts import render,HttpResponseRedirect
from Seller.models import Seller,Types,Goods,Image
import hashlib
import datetime
import os
from Qshop.settings import MEDIA_ROOT
# Create your views here.
#哈希md5加密
def setPassword(password):
    md5=hashlib.md5()
    md5.update(password.encode())
    result=md5.hexdigest()
    return result
#session对象：用来存储特定用户会话所需的属性及配置信息
#session会保存在后台数据库中，比cookis安全，字典形式
def sessionValid(fun):
    def inner(request,*args,**kwargs):
        cookie=request.COOKIES
        session=request.session.get("nickname")
        user=Seller.objects.filter(username=cookie.get("username")).first()
        if user and user.nickname==session:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/seller/login/')
    return inner
@sessionValid
def index(request):
    return render(request,"seller/index.html",locals())

def login(request):
    result = {"error": ""}
    if request.method == "POST" and request.POST:
        login_valid = request.POST.get("login_valid")
        froms = request.COOKIES.get("from")
        if login_valid == "login_valid" and froms == "http://127.0.0.1:8000/seller/login/":
            username = request.POST.get("username")
            user = Seller.objects.filter(username = username).first()
            if user:
                db_password = user.password
                password = setPassword(request.POST.get("password"))
                if db_password == password:
                    response = HttpResponseRedirect("/seller/")
                    response.set_cookie("username",user.username)
                    response.set_cookie("id", user.id)
                    request.session["nickname"] = user.nickname #设置session
                    return response
                else:
                    result["error"] = "密码错误"
            else:
                result["error"] = "用户不存在"
        else:
             result["error"] = "请查询正确的接口进行登录"
    response = render(request,"seller/login.html",{"result": result})
    response.set_cookie("from","http://127.0.0.1:8000/seller/login/")
    return response

def logout(request):
    username=request.COOKIES.get("username")
    if username:
        response=HttpResponseRedirect('/seller/login/')
        response.delete_cookie("username")
        return response
    else:
        return HttpResponseRedirect('/seller/login/')

@sessionValid
def goods_list(request):
    goodsList = Goods.objects.all()
    return render(request,"seller/goods_list.html",locals())

@sessionValid
def goods_add(request):
    postData = request.POST  # post数据
    if request.method == "POST" and request.POST:
        goods_id = postData.get("goods_id")     #商品编号
        goods_name = postData.get("goods_name")     #商品名称
        goods_price = postData.get("goods_price") #商品原价
        goods_now_price = postData.get("goods_now_price") #商品现价
        goods_num = postData.get("goods_num")   #商品库存
        goods_description = postData.get("goods_description") #商品介绍
        goods_content = postData.get("goods_content") #商品详情
        goods_show_time=datetime.datetime.now()  # 发布时间
        types = postData.get("goods_type")            #商品类型


        # 存入数据库
        t = Goods()
        t.goods_id = goods_id
        t.goods_name = goods_name
        t.goods_price = goods_price
        t.goods_now_price = goods_now_price
        t.goods_num = goods_num
        t.goods_description = goods_description
        t.goods_content = goods_content
        t.goods_show_time = goods_show_time
        t.types = Types.objects.get(id=int(types))
        t.goods_content=goods_content
        id = request.COOKIES.get("id")   #登录时创建的cookis
        if id:                          #防非浏览器访问的爬虫
            t.seller = Seller.objects.get(id=int(id))
        else:
            return HttpResponseRedirect("/seller/login/")
        t.save()
        imgs = request.FILES.getlist("userfiles")
        # 保存图片
        for index, img in enumerate(imgs):#枚举
            # 保存图片到服务器
            file_name = img.name
            file_path = "seller/images/%s_%s.%s" % (goods_name, index, file_name.rsplit(".", 1)[1])
            save_path = os.path.join(MEDIA_ROOT, file_path).replace("/", "\\")
            try:
                with open(save_path, "wb") as f:
                    for chunk in img.chunks(chunk_size=1024):
                        f.write(chunk)
                # 保存路径到数据库
                i = Image()
                i.img_adress = file_path
                i.img_label = "%s_%s" % (index, goods_name)
                i.img_description = "this is description"
                i.goods = t
                i.save()
            except Exception as e:
                print(e)
    return render(request,"seller/goods_add.html",locals())