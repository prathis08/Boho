# Generated by Django 4.0.3 on 2022-04-28 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boho', '0005_sponsors'),
    ]

    operations = [
        migrations.CreateModel(
            name='offers',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(default='')),
                ('link', models.URLField(default='')),
                ('image_link', models.CharField(default='', max_length=30)),
                ('accent_color', models.CharField(default='', max_length=30)),
            ],
        ),
    ]
