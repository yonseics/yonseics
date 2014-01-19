# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from combaragi import settings
from combaragi.community.utils import get_bomb_file_path


class Bomb(models.Model):
    user = models.ForeignKey(User)
    bombfile = models.FileField(upload_to=get_bomb_file_path)
    title = models.CharField(max_length=100, verbose_name='폭탄이름')
    uploaded = models.DateTimeField(auto_now=True)
    private = models.BooleanField()

    class Meta:
        ordering = ['-uploaded']

    def __unicode__(self):
        return self.title

    def getDueDate(self):
        return self.uploaded + timedelta(days=settings.BOMB_TIME_DAYS)


@receiver(pre_delete, sender=Bomb)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.bombfile.delete(False)


class BombAlarm(models.Model):
    bomb = models.ForeignKey(Bomb)
    time = models.DateTimeField()

    def __unicode__(self):
        return self.bomb.title + ': ' + str(self.bomb.getDueDate() - self.time) + ' before'