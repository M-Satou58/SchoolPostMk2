# Generated by Django 4.0.5 on 2022-06-18 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sp', '0055_alter_bill_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='houserule',
            name='student',
        ),
        migrations.AddField(
            model_name='houserule',
            name='student',
            field=models.ManyToManyField(to='sp.studenteconomy'),
        ),
    ]
