# Generated by Django 5.0.6 on 2024-09-01 19:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('friends', '0001_initial'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendmessage',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_received', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='friendmessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_sent', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_received', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_sent', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='profile1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships_as_profile1', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='profile2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships_as_profile2', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='removed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='removed_friendships', to='profiles.profile'),
        ),
        migrations.AddField(
            model_name='friendmessage',
            name='friendship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='friends.friendship'),
        ),
        migrations.AddConstraint(
            model_name='friendrequest',
            constraint=models.UniqueConstraint(fields=('sender', 'receiver'), name='unique_friend_request_pair'),
        ),
        migrations.AddConstraint(
            model_name='friendship',
            constraint=models.UniqueConstraint(fields=('profile1', 'profile2'), name='unique_friendship_pair'),
        ),
    ]