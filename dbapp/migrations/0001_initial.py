# Generated by Django 3.2.8 on 2021-10-14 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drawing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('text', models.TextField()),
            ],
        ),
    ]