# Generated by Django 4.1.2 on 2022-10-10 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_yookassapayment_is_pending'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referer', models.TextField(verbose_name='Источник')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Дата показа')),
            ],
        ),
    ]
