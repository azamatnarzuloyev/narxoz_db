# Generated by Django 4.2.7 on 2025-07-23 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0006_alter_attendancerecord_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unknownface',
            name='distance',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
