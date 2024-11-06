# Generated by Django 5.1.2 on 2024-10-30 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_image',
            field=models.ImageField(
                default='profile_images/default.jpg',
                upload_to='profile_images/'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='pseudo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]