# Generated by Django 3.1.5 on 2022-03-15 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boho', '0003_auto_20220310_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='totalcost',
            field=models.IntegerField(null=True),
        ),
    ]
