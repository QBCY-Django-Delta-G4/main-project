# Generated by Django 5.1.1 on 2024-09-12 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0013_remove_doctor_deleted_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='availabletime',
            options={'permissions': [('admin_available_time', 'Can add-edit-remove available time'), ('patient_available_time', 'Can view available time')]},
        ),
    ]
