# Generated by Django 3.1.2 on 2020-11-02 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20201102_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(default='test-shirt'),
            preserve_default=False,
        ),
    ]
