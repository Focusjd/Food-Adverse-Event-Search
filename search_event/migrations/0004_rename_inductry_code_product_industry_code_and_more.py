# Generated by Django 4.2 on 2023-04-19 03:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search_event', '0003_alter_foodadverseevent_consumer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='inductry_code',
            new_name='industry_code',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='inductry_name',
            new_name='industry_name',
        ),
    ]