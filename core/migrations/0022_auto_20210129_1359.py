# Generated by Django 3.1.2 on 2021-01-29 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20201112_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sport Wear'), ('OW', 'Outwear'), ('P', 'Pants'), ('O', 'Other')], max_length=2),
        ),
    ]
