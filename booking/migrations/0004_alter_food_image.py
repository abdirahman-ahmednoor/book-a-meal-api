# Generated by Django 3.2.8 on 2021-10-11 17:15

import cloudinary.models
from django.db import migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_auto_20211011_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='image',
            field=cloudinary.models.CloudinaryField(default=django.utils.timezone.now, max_length=255, verbose_name='image'),
            preserve_default=False,
        ),
    ]
