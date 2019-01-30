from django.shortcuts import render,HttpResponseRedirect
from django.http import HttpResponse
from Buyer.models import *
import hashlib,os
from Qshop.settings import MEDIA_ROOT
from Seller.models import Goods
from Seller.models import Image as SellerImage
# Create your views here.
def setPassword(password):
    md5=hashlib.md5()
    md5.update(password.encode())
    result=md5.hexdigest()
    return result

#获取cookis
def cookieValid(fun):
    def inner(request,*args,**kwargs):
        cookie = request.COOKIES
        username = cookie.get("username")
        session = request.session.get("username") #获取session
        user = Buyer.objects.filter(username = username).first()
        if user and session == username: #校验session
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/buyer/login/") #没有获取到cookis和session进行拦截
    return inner

@cookieValid
def index(request):
    data = []
    goods = Goods.objects.all() #获取所有的商品
    userid=request.COOKIES.get("id")
    buyername=Buyer.objects.get(id=userid)
    for good in goods: #循环每一个商品
        goods_img = good.image_set.first() #每个商品对于的第一个图片
        img = goods_img.img_adress.url
        data.append(
            {"id": good.id,"img": img.replace("media","static"), "name": good.goods_name, "price": good.goods_now_price}
        )
    return render(request,"buyer/index.html",{"datas": data ,"buyername":buyername})

#登录页
def login(request):
    result = {"error": ""}
    postData = request.POST
    if request.method == "POST" and request.POST:
        username = request.POST.get("username")
        user = Buyer.objects.filter(username=username).first()
        if user:
            password=setPassword(postData.get("userpass"))
            db_password=user.userpass
            if password==db_password:
                response = HttpResponseRedirect("/buyer/index/")
                response.set_cookie("username", user.username)  #设置cookis（"自己起的名字","获取的内容Buyer表里的username"）
                response.set_cookie("id", user.id)
                request.session["username"] = user.username  # 设置session，存入数据库以字典方式
                return response
            else:
                result['error']='密码错误'
        else:
            result['error']='用户名不存在'
    response = render(request, "buyer/login.html", {"result": result})
    return response


import time
import datetime
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from Buyer.models import EmailValid
import random
#随机数随机验证码
def getRandomData():
    result = str(random.randint(1000,9999))
    return result
#发送邮件
def sendMessage(request):
    result = {"staue": "error","data":""}
    if request.method == "GET" and request.GET:
        recver = request.GET.get("username")
        try:
            subject = "注册邮件"
            text_content = "验证码"
            value = getRandomData()
            html_content = """
            <div>
                <p>
                    尊敬的用户，您的用户验证码是:%s,谨防上当，请勿给他人使用。
                </p>
            </div>
            """%value
            message = EmailMultiAlternatives(subject,text_content,"18729847670@163.com",[recver])
            message.attach_alternative(html_content,"text/html") #既可以text又可以html
            message.send()
        except Exception as e:
            result["data"] = str(e)
        else:
            result["staue"] = "success"
            result["data"] = "发送成功"
            email = EmailValid()
            email.value = value
            email.times = datetime.datetime.now()
            email.email_address = recver
            email.save()
        finally:
            return JsonResponse(result)

#注册
def zhuce(request):
    result = {"statu": "error","data":""}
    if request.method == "POST" and request.POST:
        username = request.POST.get("username")  #邮箱
        code = request.POST.get("code")   #验证码
        userpass = request.POST.get("userpass")
        email = EmailValid.objects.filter(email_address = username).first()
        nickname=request.POST.get("nickname")
        userfiles=request.FILES.get('userfiles')
        if email:
            if code == email.value:
                now = time.mktime(
                    datetime.datetime.now().timetuple()
                )
                db_now = time.mktime(email.times.timetuple())
                if now - db_now >= 86400:
                    result["data"] = "验证码过期"
                    email.delete()
                else:
                    s = Buyer()
                    s.username=username
                    s.userpass=setPassword(userpass)
                    s.nickname=nickname
                    # 保存图片
                    # 保存图片到服务器
                    file_path = "seller/images/%s" % (userfiles)
                    save_path = os.path.join(MEDIA_ROOT, file_path).replace("/", "\\")
                    with open(save_path,"wb") as f:
                        for i in userfiles.chunks(): #将图片转换为二进制形式
                            f.write(i)
                    result["statu"] = "success"
                    result["data"] = "恭喜！注册成功"
                    email.delete()
                    s.save()
                    return HttpResponseRedirect("/buyer/login/")
            else:
                result["data"] = "验证码错误"
        else:
            result["data"] = "验证码不存在"
    return render(request, 'buyer/zhuce.html',locals())

#商品详情页
def goods_details(request,id):
    userid = request.COOKIES.get("id")
    buyername = Buyer.objects.get(id=userid)
    good = Goods.objects.get(id=int(id)) #一个商品
    good_img = good.image_set.first().img_adress.url.replace("media","static")

    seller = good.seller #商品对应的商铺 外键 --> 主
    goods = seller.goods_set.all() #主 --> 外
    data = []
    for g in goods:
        goods_img = g.image_set.first()
        img = goods_img.img_adress.url
        data.append(
            {"id": g.id, "img": img.replace("media","static"), "name": g.goods_name, "price": g.goods_now_price}
        )
    return render(request,"buyer/goods_details.html",locals())

from Buyer.models import BuyCar
#添加到购物车页
def carJump(request,goods_id):
    goods = Goods.objects.get(id = int(goods_id))
    id = request.COOKIES.get("id")  # 获取用户身份
    buyername=Buyer.objects.get(id=id)
    if request.method == "POST" and request.POST:
        count = request.POST.get("count") #goods_details.html 中form表单action="/buyer/carJump/
        img = request.POST.get("good_img")
        buyCar = BuyCar.objects.filter(user = int(id),goods_id = int(goods_id)).first() #查询是否存在在购物车当中
        if not buyCar: #不存在
            buyCar = BuyCar() #实例化模型
            buyCar.goods_num = int(count) #添加数量
            buyCar.goods_id = goods.id
            buyCar.goods_name = goods.goods_name
            buyCar.goods_price = goods.goods_now_price
            buyCar.user = Buyer.objects.get(id=request.COOKIES.get("id"))
            buyCar.save()
        else: #存在
            buyCar.goods_num += int(count) #数量相加
            buyCar.save()
        all_price = float(buyCar.goods_price) * int(count)
        return render(request,"buyer/buyCar_jump.html",locals())
    else:
        return HttpResponse("404 not fond")
@cookieValid
def carList(request):
    user_id=request.COOKIES.get("id") #获取用户身份
    buyername=Buyer.objects.get(id=user_id)
    #user是Buycar中的外键
    goodList = BuyCar.objects.filter(user = int(user_id)) #查询指定用户的购物车商品信息
    price_list = []
    address_list = Address.objects.filter(buyer=int(user_id))
    all=0
    for goods in goodList:
        goodpic = SellerImage.objects.filter(goods=int(goods.goods_id)).first()
        picture = goodpic.img_adress
        all_price = float(goods.goods_price) * int(goods.goods_num)
        price_list.append({"price": all_price,"goods":goods,"picture":picture}) #添加总数
        all+=all_price
    return render(request,"buyer/car_list.html",locals())

@cookieValid
def delete_goods(request,goods_id):
    id = request.COOKIES.get("id")
    goods = BuyCar.objects.filter(user = int(id),goods_id = int(goods_id))
        #对应用户id
        #对应商品id
    goods.delete()
    return HttpResponseRedirect("http://127.0.0.1:8000/buyer/carList/")

@cookieValid
def clear_goods(request):  #清空商品
    id = request.COOKIES.get("id")  #获取设置COOKIS时设置的变量名
    goods = BuyCar.objects.filter(user = int(id))
    goods.delete()
    return HttpResponseRedirect("http://127.0.0.1:8000/buyer/carList/")

def add_order(request):
    buyer_id = request.COOKIES.get("id") #用户的id
    goods_list = [] #订单商品的列表
    address_list = Address.objects.filter(buyer=int(buyer_id))
    if request.method == "POST" and request.POST:
        requestData = request.POST #请求数据
        addr = requestData.get("address") #寄送地址的id
        pay_method = requestData.get("pay_Method") #支付方式

        #获取商品信息
        all_price = 0 #总价
        for key,value in requestData.items(): #循环所有的数据
            if key.startswith("name"): #如果键以name开头，我们就认为是一条商品信息的id
                buyCar = BuyCar.objects.get(id=int(value)) #获取商品
                price = float(buyCar.goods_num) * float(buyCar.goods_price) #单条商品的总价

                all_price += price #加入总价
                goods_list.append({"price":price,"buyCar":buyCar}) #构建数据模型{"小计总价":price,"商品信息":buyCar}
        # 存入订单库
        Addr = Address.objects.get(id=int(addr)) #获取地址数据
        order = Order() #保存到订单
        #订单编号 日期 + 随机 + 订单 + id
        now = datetime.datetime.now()
        order.order_num = now.strftime("%Y-%m-%d")+str(random.randint(10000,99999))+str(order.id)
        order.order_time = now
        # 状态 未支付 1 支付成功 2 配送中 3 交易完成 4 已取消 0
        order.order_statue = 1
        order.total = all_price
        order.user = Buyer.objects.get(id = int(buyer_id))
        order.order_address = Addr
        order.save()

        for good in goods_list: #循环保存订单当中的商品
            g = good["buyCar"]
            g_o = OrderGoods()
            g_o.goods_id = g.id
            g_o.goods_name = g.goods_name
            g_o.goods_price = g.goods_price
            g_o.goods_num = g.goods_num
            g_o.goods_picture = g.goods_picture
            g_o.order = order
            g_o.save()
        return render(request,"buyer/enterOrder.html",locals())#订单页
    else:
        return HttpResponseRedirect("/buyer/carList/")

from Buyer.models import Address

def addAddress(request):  #添加地址
    if request.method == "POST" and request.POST:
        buyer_id = request.COOKIES.get("id")
        buyer_name = request.POST.get("buyer")
        buyer_phone = request.POST.get("buyer_phone")
        buyer_address = request.POST.get("buyer_address")
        db_buyer = Buyer.objects.get(id = int(buyer_id))

        addr = Address()
        addr.recver = buyer_name
        addr.phone = buyer_phone
        addr.address = buyer_address
        addr.buyer = db_buyer
        addr.save()
        return HttpResponseRedirect("/buyer/address/")
    return render(request,"buyer/addAddress.html")

def address(request):
    buyer_id = request.COOKIES.get("id")
    buyername = Buyer.objects.get(id=buyer_id)
    address_list = Address.objects.filter(buyer=int(buyer_id))
    return render(request,"buyer/address.html",locals())

def changeAddress(request,address_id):  #修改地址
    addr = Address.objects.get(id=int(address_id))
    if request.method == "POST" and request.POST:
        buyer_name = request.POST.get("buyer")
        buyer_phone = request.POST.get("buyer_phone")
        buyer_address = request.POST.get("buyer_address")

        addr.recver = buyer_name
        addr.phone = buyer_phone
        addr.address = buyer_address
        addr.save()
        return HttpResponseRedirect("/buyer/address/")
    return render(request,"buyer/addAddress.html",locals())

def delAddress(request,address_id):  #删除地址
    addr = Address.objects.get(id=int(address_id))
    addr.delete()
    return HttpResponseRedirect("/buyer/address/")



from alipay import AliPay
def pay(order_id,money):
    alipay_public_key_string = '''-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxQSqC51VCdKQPZgdeocT5rr/9oMj7HRj+CN9RduRUJh8lSTv+IhBRFmK0iBYhjXVjSSqglOnXQ6hKoFRmk81iz8WLu9VWuqfA3TGlQT2oQKxRQeQPIbqzjTGzZ+80uxmRlgGy5fbprb0X1FaCevWyV4WxTqmNQ63IwrQ8QTDdH9zcGQyu5mzsekJd8XN6D8pA0Q6oX/aAqZ3cuWIFTw6MA03H7Fj7l6lUMej7FtnX6t55oTSvi6lKcjuasNtfmyK0ZjD2GGB/A7Scgj6P2SxVLd017EwtaglNOvTv8jV8GZSH1wAd1THHkvlmf6LL+svVWbBi9OllntsD7rvyKW6IQIDAQAB
        -----END PUBLIC KEY-----'''

    app_private_key_string = '''-----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEAxQSqC51VCdKQPZgdeocT5rr/9oMj7HRj+CN9RduRUJh8lSTv+IhBRFmK0iBYhjXVjSSqglOnXQ6hKoFRmk81iz8WLu9VWuqfA3TGlQT2oQKxRQeQPIbqzjTGzZ+80uxmRlgGy5fbprb0X1FaCevWyV4WxTqmNQ63IwrQ8QTDdH9zcGQyu5mzsekJd8XN6D8pA0Q6oX/aAqZ3cuWIFTw6MA03H7Fj7l6lUMej7FtnX6t55oTSvi6lKcjuasNtfmyK0ZjD2GGB/A7Scgj6P2SxVLd017EwtaglNOvTv8jV8GZSH1wAd1THHkvlmf6LL+svVWbBi9OllntsD7rvyKW6IQIDAQABAoIBAQCRBdLpw8Eh/tXgEQW5+I5Eq+fYHEYoOrCPqgf/kRURP32NB2iBCEMKveK6s8aV3DC6uX+teUhb7nXh5NkdfirKugBpQhERYFz2XVIDxWiJsoKsblnUw/c5HI4uM+P5WrwaEZfG65xqxodxVl+xp+Etzs1yFq7bpV5XNBIDJ9978z5ZtEWOPEFf6jHaj0aP2cJViSbKYmXHJ19DwzEw5k0au3hnTZ2bbTeGZHfAO/GxVx+2v09OR5+EJRHD7xgQAGTDvVhFTealZ6RRCWRo5WpxxJ+hYU+VTJ8jwQBLFSPKb+01LII/MwOzFHPFjyHzXOAtnNQ3EcJf1KVZISbZBuYxAoGBAOZNsmPXQChT+R2Z+nXAIti2D0BmeBHhbkS8Tu2znx/xdkREB/MElMi0GwUzBS0QKvQeggEMhtbVmzyekpLVMo4/pU9Hs+oS67LzLKfID2VIdXcWn++i5lhiqi680Pl3+hHntJn/emXntaT2IFjzaYXeeO6Iy2fGdBoAUWLVQeLdAoGBANsAOBDnjle8vPkaQg9GIPuKpSzRAHJx7ZxAgFzrMpYtPoySpEiPmi5xd58Qr8HfrNalMvH4r5eLNggkiutW5sNWNogmENg8nCIIqpHOJXCFEG9sZkR+Kyw1AgMGQui5zYIoZLQcpUVboHaepDEAqJgiuPBPhIQ2nLKVs2NS+bYVAoGAN7SbbaLnFdoZ65sPBeRPiXOgBMfESy7n6SBTRxOnbaaOIL0D3zhAdLt7vao1mkzK1vl6IJ7TDqvkPKlucq226MlkRuTlE7033bUMHBk8ABeisgd68A/K/5395Agv0+e9SQ9uk8FD7do6CYivElTuNT82qRvVd2h9NLzW8rz6jtECgYA+Olu0AffiWlDf/2QR7v1kPEse5uxXmKPJqFJRFMu0/Hove2OO8q7+z2MMIbOvRR1ZiGtnciCC0R2zRp7qrDC6BH9ORHK43tAGo6vD7m2ZAVZgMs8EW01tLEq8DUVp15HbkBq9Sv5zLMv1qLJC8kr1n7gpII8o+lOgMwVcDbHC2QKBgQDk3WAo6gt9k99qgdYU778TSAu7PCBFe5S7w3XEieqfZh1qpZ4whk/46k22fVsVyG/gut/gGqUnRieAylhH7JRTWCg+eAUoC1HCftxhGqszg1kaiKqjriDJYzpTKQGa8PzNu2jvvuwrBU1vIFBGL5oXfyhaK7xhLxbdLW2ZZyFi0w==
        -----END RSA PRIVATE KEY-----'''

    # 如果在Linux下，我们可以采用AliPay方法的app_private_key_path和alipay_public_key_path方法直接读取.emp文件来完成签证
    # 在windows下，默认生成的txt文件，会有两个问题
    # 1、格式不标准
    # 2、编码不正确 windows 默认编码是gbk

    # 实例化应用
    alipay = AliPay(
        appid="2016092400585984",  # 支付宝app的id
        app_notify_url=None,  # 回调视图
        app_private_key_string=app_private_key_string,  # 私钥字符
        alipay_public_key_string=alipay_public_key_string,  # 公钥字符
        sign_type="RSA2",  # 加密方法
    )
    # 发起支付
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(money),  # 将Decimal类型转换为字符串交给支付宝
        subject="商贸商城",
        return_url="127.0.0.1:8000/carList",#完成以后返回
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 让用户进行支付的支付宝页面网址
    return "https://openapi.alipaydev.com/gateway.do?" + order_string

def callbackPay(request,order_id):
    order=Order.objects.get(id=order_id)
    o_n=order.order_num
    o_m=order.total
    v=pay(o_n,o_m)
    return HttpResponseRedirect(v)