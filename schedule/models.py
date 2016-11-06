# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from time import time
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import models
from django.utils.encoding import smart_unicode
from users.models import Location

class Course(models.Model):

    course_title = models.CharField(max_length=100, null=True, blank=True)
    course_subtitle = models.CharField(max_length=240, null=True, blank=True)
    course_length = models.CharField(max_length=3, null=True, blank=True)
    course_active = models.BooleanField(default=True)
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=True)
    course_start_time = models.TimeField(max_length=6, null=True, blank=True)
    course_end_time = models.TimeField(max_length=6, null=True, blank=True)
    course_recurring_end_date = models.DateTimeField(max_length=50, null=True, blank=True)
    course_created = models.DateTimeField(auto_now_add=True)
    course_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='course_created')
    course_age_min = models.CharField(max_length=2, null=True, blank=True, default=0)
    course_age_max = models.CharField(max_length=2, null=True, blank=True, default=99)
    white = models.BooleanField(default=True)
    red = models.BooleanField(default=True)
    yellow = models.BooleanField(default=True)
    green = models.BooleanField(default=True)
    blue = models.BooleanField(default=True)
    purple = models.BooleanField(default=True)
    brown = models.BooleanField(default=True)
    black = models.BooleanField(default=True)
    practice_min = models.CharField(max_length=4, null=True, blank=True, default=0)
    course_credit = models.CharField(max_length=3, null=True, blank=True, default=0)
    max_student = models.CharField(max_length=2, null=True, blank=True)
    course_location = models.ForeignKey(Location, related_name='location_course', blank=True, null=True)
    course_private = models.BooleanField(default=False)
    course_private_student = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __unicode__(self):
        return smart_unicode(self.course_title)


class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, null=True, blank=True)
    student = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='course_student', blank=True)
    schedule_date = models.DateField(max_length=50, null=True, blank=True)
    schedule_start_time = models.TimeField(max_length=6, null=True, blank=True)
    schedule_end_time = models.TimeField(max_length=6, null=True, blank=True)
    schedule_recurring_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_recurring', blank=True)
    schedule_created = models.DateTimeField(auto_now_add=True)
    schedule_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='schedule_created', null=True, blank=True)
    schedule_updated = models.DateTimeField(auto_now_add=True)
    schedule_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='schedule_updated', null=True, blank=True)
    schedule_canceled = models.BooleanField(default=False)

    def __unicode__(self):
        return smart_unicode(self.course, self.schedule_date)
        