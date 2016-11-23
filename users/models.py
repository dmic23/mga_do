# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager
from django.core.files.storage import default_storage
from django.db import models
from django.utils.encoding import smart_unicode
from time import time

def get_upload_file_name(instance, filename):

    return settings.UPLOAD_FILE_PATTERN % (str(time()).replace('.','_'), filename)

class Location(models.Model):

    name = models.CharField(max_length=50, null=True, blank=True)
    addr1 = models.CharField(max_length=50, null=True, blank=True)
    addr2 = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    phone_main = models.CharField(max_length=20, null=True, blank=True)
    phone_other = models.CharField(max_length=20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    location_created = models.DateTimeField(auto_now_add=True)
    location_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='location_created_user')

    def __unicode__(self):
        return smart_unicode(self.name)

class StudentNote(models.Model):

    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='student_note')
    note = models.TextField()
    note_created = models.DateTimeField(auto_now_add=True)
    note_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='note_created_user')
    note_updated = models.DateTimeField(auto_now=True)
    note_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='note_updated_user', null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.id)

class StudentPlan(models.Model):

    plan_title = models.CharField(max_length=50, null=True, blank=True)
    plan_description = models.TextField(null=True, blank=True)
    plan_created = models.DateTimeField(auto_now_add=True)
    plan_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plan_created_user', null=True, blank=True)
    plan_updated = models.DateTimeField(auto_now_add=True)
    plan_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plan_updated_user', null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.plan_title)

class StudentPlanSection(models.Model):

    student_plan = models.ForeignKey(StudentPlan, related_name="plan_section")
    section_week = models.CharField(max_length=3, null=True, blank=True)
    section_number = models.CharField(max_length=3, null=True, blank=True)
    section_title = models.CharField(max_length=50, blank=True)
    section_description = models.TextField(blank=True)
    section_notes = models.TextField(blank=True)
    section_created = models.DateTimeField(auto_now_add=True)
    section_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='section_created_user', null=True, blank=True)
    section_updated = models.DateTimeField(auto_now_add=True)
    section_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='section_updated_user', null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.section_title)    

class StudentPlanFile(models.Model):

    plan_section = models.ForeignKey(StudentPlanSection, related_name='plan_section_file', null=True, blank=True)
    plan_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True)
    plan_file_name = models.CharField(max_length=100, null=True, blank=True)
    plan_file_created = models.DateTimeField(auto_now_add=True)
    plan_file_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plan_file_added_user', null=True, blank=True)
    plan_file_updated = models.DateTimeField(auto_now=True)
    plan_file_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plan_file_updated_user', null=True, blank=True)


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **kwargs):
        if not username:
            raise ValueError('Users must have a valid username.')

        # if not email:
        #     raise ValueError('Users must have a valid email.')

        user = self.model(
            username=username,
            first_name=kwargs.get('first_name'), last_name=kwargs.get('last_name'),
            email=kwargs.get('email'), date_of_birth=kwargs.get('date_of_birth'))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password, **kwargs):
        user = self.create_user(username=username, email=email, password=password)
        user.username = username
        user.email = email
        user.is_admin = True
        user.is_active = True
        user.save()

        return user

class User(AbstractBaseUser):
    USER_RANK = (
        ('1', 'White'),
        ('2', 'Yellow'),
        ('3', 'Orange'),
        ('4', 'Green'),
        ('5', 'Blue'),
        ('6', 'Purple'),
        ('7', 'Red'),
        ('8', 'Brown'),
        ('9', 'Black'),
    )
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    user_pic = models.FileField(upload_to=get_upload_file_name, null=True, blank=True, default='blank_user.png')
    user_created = models.DateTimeField(auto_now_add=True)
    user_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_user', null=True, blank=True, unique=False)
    user_updated = models.DateTimeField(auto_now=True)
    user_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='updated_user', null=True, blank=True, unique=False)
    location = models.ForeignKey(Location, related_name='user_location', null=True, blank=True)
    play_level = models.CharField(max_length=20, choices=USER_RANK, null=True, blank=True, default='1')
    date_of_birth = models.DateField(max_length=50, null=True, blank=True)
    user_credit = models.CharField(max_length=4, null=True, blank=True, default=0)
    recurring_credit = models.CharField(max_length=2, null=True, blank=True, default=0)
    course_reminder = models.BooleanField(default=True)
    practice_reminder = models.BooleanField(default=True)
    user_update = models.BooleanField(default=True)
    student_plan = models.ForeignKey(StudentPlan, related_name="plan_student", null=True, blank=True)


    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return smart_unicode(self.username)

    def get_full_name(self):
        return ' '.join([self.first_name, self.last_name])

    def get_short_name(self):
        return self.first_name

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin 


class StudentGoal(models.Model):

    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='student_goal') 
    goal = models.CharField(max_length=250)
    goal_target_date = models.DateTimeField(max_length=50, null=True, blank=True)
    goal_complete = models.BooleanField(default=False)
    goal_complete_date = models.DateTimeField(max_length=50, null=True, blank=True)
    goal_notes = models.TextField(null=True, blank=True)
    goal_created = models.DateTimeField(auto_now_add=True)
    goal_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='goal_created_user')
    goal_updated = models.DateTimeField(auto_now=True)
    goal_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='goal_updated_user', null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.goal)

class StudentPracticeLog(models.Model):

    PRACTICE_CATEGORIES = (
        ('LEAD_TECHNIQUE', 'Lead Technique'),
        ('RHYTHM_TECHNIQUE', 'Rhythm Technique'),
        ('FRETBOARD', 'Fretboard Knowledge'),
        ('THEORY', 'Music Theory Concepts'),
        ('REPERTOIRE', 'Songs and Repertoire'),
        ('CREATIVITY', 'Creativity'),
    )
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='student_log')
    practice_category = models.CharField(max_length=20, choices=PRACTICE_CATEGORIES, null=True, blank=True)
    practice_item = models.CharField(max_length=50)
    practice_time = models.CharField(max_length=50, null=True, blank=True)
    practice_speed = models.CharField(max_length=50, null=True, blank=True)
    practice_notes = models.TextField(null=True, blank=True)
    practice_date = models.DateTimeField(max_length=50, null=True, blank=True)
    practice_item_created = models.DateTimeField(auto_now_add=True)
    practice_item_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='log_created_user')
    practice_item_updated = models.DateTimeField(auto_now=True)
    practice_item_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='log_updated_user', null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.practice_item)

class StudentObjective(models.Model):

    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='student_objective')
    objective = models.CharField(max_length=250)
    objective_complete = models.BooleanField(default=False)
    objective_complete_date = models.DateTimeField(max_length=50, null=True, blank=True)
    objective_notes = models.TextField(null=True, blank=True)
    objective_visible = models.BooleanField(default=False)
    objective_priority = models.CharField(max_length=3, null=True, blank=True)
    objective_created = models.DateTimeField(auto_now_add=True)
    objective_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='objective_created_user')
    objective_updated = models.DateTimeField(auto_now=True)
    objective_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='objective_updated_user', null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.objective)

class StudentWishList(models.Model):

    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='student_wishlist')
    wish_item = models.CharField(max_length=250)
    wish_item_complete = models.BooleanField(default=False)
    wish_item_complete_date = models.DateTimeField(max_length=50, null=True, blank=True)
    wish_item_notes = models.TextField(null=True, blank=True)
    wish_item_created = models.DateTimeField(auto_now_add=True)
    wish_item_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wish_item_created_user')
    wish_item_updated = models.DateTimeField(auto_now_add=True)
    wish_item_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wish_item_updated_user', null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.wish_item)

class StudentMaterial(models.Model):

    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='student_material', null=True, blank=True)
    student_group = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_student', blank=True)
    file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True)
    material_name = models.CharField(max_length=50, null=True, blank=True)
    material_notes = models.TextField(null=True, blank=True)
    material_added = models.DateTimeField(auto_now_add=True)
    material_added_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='material_added_user', null=True, blank=True)
    material_updated = models.DateTimeField(auto_now=True)
    material_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='material_updated_user', null=True, blank=True)

class StudentEmail(models.Model):

    MAIL_TYPE = ( 
        ('CRE', 'User Created'),
        ('ACT', 'User Active'),
        ('UPD', 'Account Updated'),
        ('PRACT', 'User Practice Reminder'),
        ('SCHED', 'Course Scheduled'),
        ('CNCL', 'Course Cancelled'),
        ('REMD', 'Course Scheduled Reminder')
    )
    mail_type = models.CharField(max_length=8, choices=MAIL_TYPE, null=True, blank=True)
    from_email = models.EmailField(null=True, blank=True)
    cc = models.EmailField(null=True, blank=True)
    bcc = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=250, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    footer = models.TextField(null=True, blank=True)

