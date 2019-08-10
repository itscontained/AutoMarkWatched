# Generated by Django 2.2.4 on 2019-08-10 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amw', '0008_plexmediaserver_plexuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='plexuser',
            name='current_server',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_users', to='amw.PlexMediaServer'),
        ),
        migrations.AlterField(
            model_name='plexuser',
            name='servers',
            field=models.ManyToManyField(blank=True, related_name='associated_users', to='amw.PlexMediaServer'),
        ),
    ]