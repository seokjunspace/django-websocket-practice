# Generated by Django 3.1.4 on 2021-01-05 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='keyword',
            field=models.CharField(max_length=120, null=True),
        ),
    ]
