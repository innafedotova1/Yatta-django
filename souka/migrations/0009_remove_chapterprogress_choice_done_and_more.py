# Generated by Django 5.2 on 2025-06-07 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('souka', '0008_alter_choice_chapter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chapterprogress',
            name='choice_done',
        ),
        migrations.RemoveField(
            model_name='chapterprogress',
            name='test_done',
        ),
        migrations.AddField(
            model_name='chapterprogress',
            name='choice_1_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='chapterprogress',
            name='choice_2_done',
            field=models.BooleanField(default=False),
        ),
    ]
