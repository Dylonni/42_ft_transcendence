# Generated by Django 5.0.6 on 2024-07-03 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='fortytwo_id',
            field=models.CharField(blank=True, editable=False, help_text='Unique identifier for the user from 42.', null=True, verbose_name='42 id'),
        ),
    ]
