# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from schedule.models import CourseSchedule
from users.models import User, StudentPracticeLog, StudentEmail


@shared_task
def send_basic_email(user_id, mail_type):

    user = User.objects.get(id=user_id)
    email = StudentEmail.objects.get(mail_type=mail_type)
    template = 'email/basic_email.html'

    to = [user.email]
    from_email = email.from_email
    cc = [email.cc]
    bcc = [email.bcc]
    subject = email.subject

    html_content = render_to_string(template, {'user': user, 'title': email.title, 'body': email.body, 'footer': email.footer})
    text_content = strip_tags(html_content)  
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to, bcc, cc=cc)
    msg.attach_alternative(html_content, 'text/html')

    msg.send()

@shared_task
def send_practice_reminder():

    prac_since = timezone.now() - timezone.timedelta(days=3, hours=5)
    user_practice = User.objects.filter(is_active=True).exclude(student_log__practice_date__gt=prac_since).distinct() 
    email = StudentEmail.objects.get(mail_type='PRACT')
    template = 'email/basic_email.html'    
    
    for user in user_practice:
        to = [user.email]
        from_email = email.from_email
        cc = [email.cc]
        bcc = [email.bcc]
        subject = email.subject

        html_content = render_to_string(template, {'user': user, 'title': email.title, 'body': email.body, 'footer': email.footer})
        text_content = strip_tags(html_content)  
        
        msg = EmailMultiAlternatives(subject, text_content, from_email, to, bcc, cc=cc)
        msg.attach_alternative(html_content, 'text/html')

        msg.send()


@shared_task
def send_schedule_course_confirm(course_id, user_id):
    sched_course = CourseSchedule.objects.get(id=course_id)
    user = User.objects.get(id=user_id)
    email = StudentEmail.objects.get(mail_type='SCHED')
    template = 'email/course_scheduled_email.html'

    to = [user.email]
    from_email = email.from_email
    cc = [email.cc]
    bcc = [email.bcc]
    subject = email.subject

    html_content = render_to_string(template, {'user': user, 'title': email.title, 'body': email.body, 'footer': email.footer, 'sched_course': sched_course})
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to, bcc, cc=cc)
    msg.attach_alternative(html_content, 'text/html')

    msg.send()


@shared_task
def send_schedule_course_cancel(user_id, title, date, time):
    user = User.objects.get(id=user_id)
    email = StudentEmail.objects.get(mail_type='CNCL')
    template = 'email/course_scheduled_email.html'
    sched_course = {
        'course': {'course_title': title},
        'schedule_date': date, 
        'schedule_start_time': time,
    }

    to = [user.email]
    from_email = email.from_email
    cc = [email.cc]
    bcc = [email.bcc]
    subject = email.subject

    html_content = render_to_string(template, {'user': user, 'title': email.title, 'body': email.body, 'footer': email.footer, 'sched_course': sched_course})
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to, bcc, cc=cc)
    msg.attach_alternative(html_content, 'text/html')

    msg.send()


@shared_task
def send_schedule_course_reminder():
    date_to = timezone.now() + timezone.timedelta(hours=21)
    sched_courses = CourseSchedule.objects.filter(schedule_date__range=[timezone.now(), date_to]).distinct()
    email = StudentEmail.objects.get(mail_type='REMD')
    template = 'email/course_scheduled_email.html'

    for sched_course in sched_courses: 
        for user in sched_course.student.all():
            if user.is_active:

                to = [user.email]
                from_email = email.from_email
                cc = [email.cc]
                bcc = [email.bcc]
                subject = email.subject

                html_content = render_to_string(template, {'user': user, 'title': email.title, 'body': email.body, 'footer': email.footer, 'sched_course': sched_course})
                text_content = strip_tags(html_content)
                
                msg = EmailMultiAlternatives(subject, text_content, from_email, to, bcc, cc=cc)
                msg.attach_alternative(html_content, 'text/html')

                msg.send()


@shared_task
def update_recurring_credits():
    students = User.objects.filter(is_active=True)
    for student in students:
        student.user_credit = int(student.recurring_credit)
        student.save()


@shared_task
def update_recurring_schedule():
    today = datetime.date.today()
    next_scheduled_date = today + datetime.timedelta(days=7)
    daily_courses = CourseSchedule.objects.filter(schedule_date=today).exclude(schedule_recurring_user=None)
    for sched_course in daily_courses:
        for student in sched_course.schedule_recurring_user.all():
            if student.is_active:
                # if int(student.user_credit) > int(sched_course.course.course_credit):
                new_course_sched, created = CourseSchedule.objects.get_or_create(course=sched_course.course, schedule_date=next_scheduled_date, schedule_start_time=sched_course.schedule_start_time, schedule_end_time=sched_course.schedule_end_time)
                new_course_sched.student.add(student)
                new_course_sched.schedule_recurring_user.add(student)
                new_course_sched.save()
                student.user_credit = int(student.user_credit) - int(sched_course.course.course_credit)
                student.save()