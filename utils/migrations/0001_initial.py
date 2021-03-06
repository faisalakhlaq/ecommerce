# Generated by Django 3.1.2 on 2021-01-29 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Last Name')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Title')),
                ('is_company', models.BooleanField(default=False, verbose_name='Is Company')),
                ('company_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Company Name')),
                ('cvr', models.CharField(blank=True, max_length=20, null=True)),
                ('contact_person_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Contact Person Name')),
                ('street', models.CharField(blank=True, max_length=255, null=True, verbose_name='Street')),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='City')),
                ('postcode', models.CharField(blank=True, max_length=50, null=True, verbose_name='Post Code')),
                ('country', models.CharField(blank=True, max_length=255, null=True, verbose_name='Country')),
                ('phone', models.CharField(blank=True, max_length=50, null=True, verbose_name='Phone')),
                ('mobile', models.CharField(blank=True, max_length=50, null=True, verbose_name='Mobile')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
            ],
        ),
    ]
