# Generated by Django 5.1.1 on 2024-09-15 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0017_alter_doctor_specializations_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='image',
            field=models.ImageField(blank=True, default='media/empty.jpg', null=True, upload_to='media/%Y-%m-%d'),
        ),
    ]
