# Generated by Django 5.0.1 on 2024-01-21 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_subscriber_subscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100, null=True)),
                ('pwd', models.CharField(max_length=50, null=True)),
                ('mobile', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('is_active', models.BooleanField(default=False)),
                ('detail', models.TextField()),
                ('img', models.ImageField(upload_to='trainers/')),
                ('salary', models.IntegerField(default=0)),
                ('facebook', models.CharField(max_length=200, null=True)),
                ('twitter', models.CharField(max_length=200, null=True)),
                ('pinterest', models.CharField(max_length=200, null=True)),
                ('youtube', models.CharField(max_length=200, null=True)),
            ],
        ),
    ]
