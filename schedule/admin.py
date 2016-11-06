from django.contrib import admin
from schedule.models import Course, CourseSchedule

class CourseAdmin(admin.ModelAdmin):

    class Meta:
        model = Course

    list_display = ('course_title', 'course_active', 'course_location', 'course_start_time', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'course_private',)
    list_filter = ('course_title', 'course_location', 'course_start_time', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'course_active', 'course_private',)
    ordering = ('course_title',)
    filter_horizontal = ()

    fieldsets = (
        ('Course Details', {'fields': ('course_title', 'course_subtitle', 'course_active',)}),
        ('Course Availability', {'fields': ('course_location', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'course_start_time', 'course_end_time', 'course_recurring_end_date',)}),
        ('Stundent Requirements', {'fields': ('course_age_min', 'course_age_max', 'white', 'red', 'yellow', 'green',
            'blue', 'purple', 'brown', 'black', 'practice_min',)}),
        ('Course Extra', {'fields': ('max_student', 'course_credit', 'course_private', 'course_private_student', 'course_created_by',)}),
    )

admin.site.register(Course, CourseAdmin)

class CourseScheduleAdmin(admin.ModelAdmin):

    class Meta:
        model = CourseSchedule

    list_display = ('course', 'schedule_date', 'schedule_start_time', 'course_location',)
    ordering = ('-schedule_date', '-schedule_start_time', 'course',)
    readonly_fields = ('course_location',)

    def course_location(self, obj):
        return obj.course.course_location

admin.site.register(CourseSchedule, CourseScheduleAdmin)

