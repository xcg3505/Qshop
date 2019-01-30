from django.db import models

# Create your models here.

class Buyer(models.Model):

    username=models.EmailField()  #邮箱
    userpass=models.CharField(max_length=32) #密码
    nickname=models.CharField(max_length=32) #昵称
    userfiles = models.ImageField(upload_to="images")

class Image(models.Model):         #图片
    img_adress = models.ImageField(upload_to = "images")
    img_label = models.CharField(max_length = 32)
    img_description= models.TextField()

class EmailValid(models.Model):
    value = models.CharField(max_length = 32)
    email_address = models.EmailField()
    times = models.DateTimeField()

class BuyCar(models.Model):
    goods_id = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_picture = models.ImageField(upload_to="images")
    goods_num = models.IntegerField()
    user = models.ForeignKey(Buyer,on_delete = True)

class Address(models.Model):
    address = models.TextField()
    phone = models.CharField(max_length=32)
    recver = models.CharField(max_length=32)
    buyer = models.ForeignKey(Buyer, on_delete=True) #对应买家的信息

class Order(models.Model): #买家订单
    order_num=models.CharField(max_length=32)
    order_time=models.DateTimeField()
    order_statue=models.CharField(max_length=32)#订单的状态
    total=models.FloatField() #订单总价
    user= models.ForeignKey(Buyer,on_delete=True)#对应用户的信息信息
    order_address=models.ForeignKey(Address,on_delete=True)#对应地址的信息

class OrderGoods(models.Model): #商品订单
    goods_id=models.IntegerField()
    goods_name=models.CharField(max_length=32)
    goods_price=models.FloatField()
    goods_num=models.IntegerField()
    goods_picture=models.ImageField(upload_to='images')
    order=models.ForeignKey(Order,on_delete=True) #订单的信息

