# Generated by Django 3.1.2 on 2020-11-02 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_item_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='Test Migration Decsription'),
            preserve_default=False,
        ),
    ]
