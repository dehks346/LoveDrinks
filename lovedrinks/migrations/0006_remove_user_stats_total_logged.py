# Generated by Django 5.1.6 on 2025-05-11 10:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lovedrinks', '0005_remove_user_stats_top_5_drinks_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_stats',
            name='total_logged',
        ),
    ]
