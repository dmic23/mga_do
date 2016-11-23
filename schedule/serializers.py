# -*- coding: utf-8 -*-
from datetime import date
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from schedule.models import Course, CourseSchedule
from users.serializers import SimpleUserSerializer, LocationSerializer
from users.tasks import send_schedule_course_confirm

class CourseSerializer(serializers.ModelSerializer):
    course_location = LocationSerializer(required=False)

    class Meta:
        model = Course
        fields = ('id', 'course_title', 'course_subtitle', 'course_length',  'course_start_time', 'course_end_time','course_created', 'course_created_by', 'course_age_min', 'course_age_max',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'practice_min', 'course_credit', 'max_student', 'course_private', 'course_private_student',
            'white', 'red', 'yellow', 'green', 'blue', 'purple', 'brown', 'black', 'course_location',)


class CourseScheduleSerializer(serializers.ModelSerializer):
    course = CourseSerializer(required=False)
    student = SimpleUserSerializer(many=True, required=False)
    schedule_created_by = serializers.CharField(required=False)
    schedule_recurring_user = serializers.PrimaryKeyRelatedField(many=True, read_only=True, required=False)

    class Meta:
        model = CourseSchedule
        fields = ('id', 'course', 'student', 'schedule_date', 'schedule_start_time', 'schedule_end_time', 'schedule_created', 'schedule_created_by', 'schedule_updated', 'schedule_updated_by', 'schedule_recurring_user',)

    def create(self, validated_data):
        student = validated_data.pop('student')
        user = validated_data.pop('user')
        recurring = validated_data.pop('recurring')
        course_schedule, created = CourseSchedule.objects.get_or_create(**validated_data)
        if student not in course_schedule.student.all():
            if course_schedule.student.count() < int(course_schedule.course.max_student):
                course_schedule.student.add(student)
                course_schedule.save()
                send_schedule_course_confirm.delay(course_schedule.id, student.id)
                credit = int(student.user_credit) - int(course_schedule.course.course_credit)
                student.user_credit = credit
                student.save()
                if recurring:
                    course_schedule.schedule_recurring_user.add(user)
                    course_schedule.save()
        if created:
            course_schedule.schedule_created_by = user
        return course_schedule