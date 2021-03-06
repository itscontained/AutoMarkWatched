from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from plexapi.myplex import MyPlexAccount


class PlexMediaServer(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class TVShow(models.Model):
    title = models.CharField(max_length=200)
    silenced = models.BooleanField()
    continuing = models.BooleanField()
    tvdbid = models.IntegerField()
    banner_url = models.CharField(max_length=20, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class PlexUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    authenticationToken = models.CharField(max_length=200, blank=True)
    servers = models.ManyToManyField(PlexMediaServer, blank=True, related_name='associated_users')
    current_server = models.ForeignKey(PlexMediaServer, on_delete=models.SET_NULL, null=True,
                                       related_name='current_users')

    def __str__(self):
        return self.user.username


class Scheduling(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    populate = models.CharField(max_length=200, default="0 2 * * *")
    sync = models.CharField(max_length=200, default="0 4 * * 6")
    mark_watched = models.CharField(max_length=200, default="*/15 * * * *")

    def __str__(self):
        return self.mark_watched


def authenticate(username, password):
    account = MyPlexAccount(username, password)
    return account


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PlexUser.objects.create(user=instance)
        Scheduling.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.plexuser.save()
    instance.scheduling.save()


@receiver(user_logged_in, sender=User)
def post_login(sender, user, request, **kwargs):
    plex_account = authenticate(user, request.POST['password'])
    u = User.objects.get(username=user)
    u.plexuser.authenticationToken = plex_account.authenticationToken
    account_servers = [s.name for s in plex_account.resources() if 'server' in s.provides]
    for s in account_servers:
        if not u.plexuser.servers.all().filter(name=s):
            pms = PlexMediaServer.objects.all().filter(name=s) or [PlexMediaServer.objects.create(name=s)]
            u.plexuser.servers.add(pms[0])
    for s in u.plexuser.servers.all():
        if s.name not in account_servers:
            u.plexuser.servers.remove(s)
    u.plexuser.save()
