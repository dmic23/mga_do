# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import models
from django.utils.encoding import smart_unicode
from time import time
from users.models import get_upload_file_name


class Category(models.Model):
    category = models.CharField(max_length=50)
    category_created = models.DateTimeField(auto_now_add=True)
    category_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='category_created_user')

    def __unicode__(self):
        return smart_unicode(self.category)

class Topic(models.Model):
    topic_category = models.ForeignKey(Category, related_name='category_topic')
    topic = models.CharField(max_length=50)
    topic_created = models.DateTimeField(auto_now_add=True)
    topic_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='topic_created_user')

    def __unicode__(self):
        return smart_unicode(self.topic)

class Message(models.Model):
    message_topic = models.ForeignKey(Topic, related_name='topic_message')
    message_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_message')
    message = models.TextField(null=True, blank=True)
    message_created = models.DateTimeField(auto_now_add=True)
    message_visible = models.BooleanField(default=True)

    def __unicode__(self):
        return smart_unicode(self.message)

class MessageFile(models.Model):
    message = models.ForeignKey(Message, related_name='file_message')
    message_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True)
    message_file_created = models.DateTimeField(auto_now_add=True)
    message_file_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='file_user')

    def __unicode__(self):
        return smart_unicode(self.message_file)
