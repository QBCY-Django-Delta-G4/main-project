# Generated by Django 5.1.1 on 2024-09-10 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_doctor_deleted_at_doctor_deleted_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='deleted_by',
        ),
    ]
