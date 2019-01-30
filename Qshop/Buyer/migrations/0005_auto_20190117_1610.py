# Generated by Django 2.1.5 on 2019-01-17 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Buyer', '0004_auto_20190116_2159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=32)),
                ('recver', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_num', models.CharField(max_length=32)),
                ('order_time', models.DateTimeField()),
                ('order_statue', models.CharField(max_length=32)),
                ('order_address', models.ForeignKey(on_delete=True, to='Buyer.Address')),
            ],
        ),
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goods_id', models.IntegerField()),
                ('goods_name', models.CharField(max_length=32)),
                ('goods_price', models.FloatField()),
                ('goods_num', models.IntegerField()),
                ('goods_picture', models.ImageField(upload_to='images')),
                ('order', models.ForeignKey(on_delete=True, to='Buyer.Order')),
            ],
        ),
        migrations.AlterField(
            model_name='buycar',
            name='goods_picture',
            field=models.ImageField(upload_to='images'),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='userfiles',
            field=models.ImageField(upload_to='images'),
        ),
        migrations.AlterField(
            model_name='image',
            name='img_adress',
            field=models.ImageField(upload_to='images'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=True, to='Buyer.Buyer'),
        ),
        migrations.AddField(
            model_name='address',
            name='buyer',
            field=models.ForeignKey(on_delete=True, to='Buyer.Buyer'),
        ),
    ]
