# -*- coding: utf-8 -*-
import json
import datetime
import pytz
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions, status, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from schedule.models import Course, CourseSchedule
from schedule.serializers import CourseSerializer, CourseScheduleSerializer
from users.models import User, StudentPracticeLog
from users.tasks import send_schedule_course_cancel


class CourseViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, id=None):
        if self.request.user.is_admin:
            queryset = Course.objects.filter(course_active=True).exclude(course_recurring_end_date__lt=timezone.now())
        else:
            queryset = Course.objects.filter(course_active=True).exclude(Q(course_private=True) & ~Q(course_private_student=self.request.user)).exclude(course_recurring_end_date__lt=timezone.now())
        serializer = CourseSerializer(queryset, many=True)
        return Response(serializer.data)        
    

class CourseScheduleViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = CourseSchedule.objects.all()
    serializer_class = CourseScheduleSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, id=None):
        if not self.request.user.is_admin:
            queryset = CourseSchedule.objects.filter(student=self.request.user).exclude(schedule_date__lt=timezone.now())   
        else:
            queryset = CourseSchedule.objects.all()
        serializer = CourseScheduleSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if serializer.is_valid():
            course_id = self.request.data.pop('course_id')
            course = Course.objects.get(id=course_id)
            user_id = self.request.data.pop('student_id')
            student = User.objects.get(id=user_id)
            recurring = self.request.data.pop('recurring')
            serializer.save(course=course, student=student, user=self.request.user, recurring=recurring, **self.request.data)


class RemoveCourseScheduleViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = CourseSchedule.objects.all()
    serializer_class = CourseScheduleSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_update(self, serializer):
        if serializer.is_valid():
            course_id = self.request.data.pop('course_id')
            sched_id = self.request.data.pop('schedule')
            user_id = self.request.data.pop('student_id')
            student = User.objects.get(id=user_id)
            recurring = self.request.data.pop('recurring')
            instance = serializer.save()
            if student in instance.student.all():
                title = str(instance.course.course_title)
                date = str(instance.schedule_date)
                time = instance.schedule_start_time.strftime("%I:%M %p") 
                send_schedule_course_cancel.apply_async((student.id, title, date, time))
                instance.student.remove(student)
                start_date = datetime.datetime.combine(instance.schedule_date, instance.schedule_start_time)
                if start_date > datetime.datetime.now() + datetime.timedelta(hours=24):
                    student.user_credit = int(student.user_credit) + int(instance.course.course_credit)
                    student.save()
                if not recurring:
                    instance.schedule_recurring_user.remove(student)
                else:
                    today = datetime.date.today()
                    next_scheduled_date = today + datetime.timedelta(days=7)
                    recurring_course, created = CourseSchedule.objects.get_or_create(course=instance.course, schedule_date=next_scheduled_date, schedule_start_time=instance.schedule_start_time, schedule_end_time=instance.schedule_end_time, schedule_created_by=self.request.user)
                    recurring_course.student.add(student)
                    recurring_course.schedule_recurring_user.add(student)
                    recurring_course.save()
            if instance.student.count() == 0:
                course_schedule = CourseSchedule.objects.get(id=instance.id)
                course_schedule.delete()
            else:  
                instance.save()
