from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from users.models import User, Location, StudentNote, StudentGoal, StudentPracticeLog, StudentObjective, StudentWishList, StudentMaterial, StudentEmail, StudentPlan, StudentPlanSection, StudentPlanFile

class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'username')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(label= ("New Password"),
        help_text= ("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "here: <a href=\"/password_reset/\"> ---> CLICK HERE <-- </a>"))

    class Meta:
        model = User
        fields = ('email', 'password', 'username')

    def clean_password(self):

        return self.initial["password"]

class LocationAdmin(admin.ModelAdmin):

    class Meta:
        model = Location

    list_display = ('name', 'addr1', 'city',)
    list_filter = ('name', 'addr1', 'city',)
    ordering = ('city',)

admin.site.register(Location, LocationAdmin)

class StudentNoteAdmin(admin.ModelAdmin):

    class Meta:
        model = StudentNote

    list_display = ('student', 'note', 'note_created',)
    list_filter = ('student', 'note', 'note_created',)
    ordering = ('-note_created',)

admin.site.register(StudentNote, StudentNoteAdmin)

class StudentEmailAdmin(admin.ModelAdmin):

    class Meta:
        model = StudentEmail

    list_display = ('mail_type', 'subject',)

admin.site.register(StudentEmail, StudentEmailAdmin)

class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    class Meta:
        model = User

    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'user_created', 'play_level',)
    list_filter = ('is_active', 'username', 'first_name', 'last_name', 'user_created', 'play_level', 'is_admin',)
    readonly_fields = ('user_created', 'user_updated', 'last_login',)

    fieldsets = (
        ('Authorization and Login info', {'fields': ('username', 'password',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'location', 'play_level', 'user_pic', 'recurring_credit', 'user_credit', 'student_plan',)}),
        (None, {'fields': ('last_login', 'user_created_by', 'user_created', 'user_updated_by', 'user_updated',)}),
        ('Permissions', {'fields': ('is_admin', 'is_active',)}),
    )

    add_fieldsets = (
        ('Authorization and Login info', {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'location', 'play_level', 'user_pic',)}),
        (None, {'fields': ('user_created_by', 'user_created', 'user_updated_by', 'user_updated',)}),
        ('Permissions', {'fields': ('is_admin', 'is_active',)}),
    )

    ordering = ('-user_created',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)

admin.site.unregister(Group)

class StudentGoalAdmin(admin.ModelAdmin):

    class Meta:
        model = StudentGoal

    list_display = ('student', 'goal_target_date', 'goal_complete', 'goal_complete_date', 'goal',)
    list_filter = ('student', 'goal_target_date', 'goal_complete', 'goal_complete_date', 'goal_created',)
    ordering = ('-goal_created',)
    filter_horizontal = ()

admin.site.register(StudentGoal, StudentGoalAdmin)

class StudentObjectiveAdmin(admin.ModelAdmin):

    class Meta:
        model = StudentObjective

    list_display = ('student', 'objective_created', 'objective', 'objective_complete',)
    list_filter = ('student', 'objective_created', 'objective_complete', 'objective_complete_date',)
    ordering = ('-objective_created',)
    filter_horizontal = ()

admin.site.register(StudentObjective, StudentObjectiveAdmin)

class StudentPracticeLogAdmin(admin.ModelAdmin):

    class Meta:
        model = StudentPracticeLog

    list_display = ('student', 'practice_date', 'practice_category', 'practice_item', 'practice_time', 'practice_speed',)
    list_filter = ('student', 'practice_date', 'practice_category', 'practice_time', 'practice_speed', 'practice_item_created',)
    ordering = ('-practice_item_created',)
    filter_horizontal = ()

admin.site.register(StudentPracticeLog, StudentPracticeLogAdmin)

class StudentWishListAdmin(admin.ModelAdmin):

    class Meta:
        model = StudentWishList

    list_display = ('student', 'wish_item_created', 'wish_item', 'wish_item_complete', 'wish_item_complete_date',)
    list_filter = ('student', 'wish_item_created', 'wish_item', 'wish_item_complete',)
    filter_horizontal = ()

admin.site.register(StudentWishList, StudentWishListAdmin)

class StudentMaterialAdmin(admin.ModelAdmin):

    class Meta:
        model = StudentMaterial

    list_display = ('student', 'material_name', 'material_added', 'material_added_by',)
    list_filter = ('student', 'material_name', 'material_added', 'material_added_by',)
    ordering = ('-material_added',)
    filter_horizontal = ()

admin.site.register(StudentMaterial, StudentMaterialAdmin)

class StudentPlanFileInLine(admin.StackedInline):
    model = StudentPlanFile
    extra = 0

class StudentPlanSectionAdmin(admin.ModelAdmin):

    inlines = [
        StudentPlanFileInLine,
    ]

    class Meta:
        model = StudentPlanSection

    list_display = ('student_plan', 'section_week', 'section_number', 'section_title',)
    list_filter = ('student_plan', 'section_week', 'section_number', 'section_title',)
    # ordering = ()

admin.site.register(StudentPlanSection, StudentPlanSectionAdmin)

class StudentPlanSectionInLine(admin.StackedInline):
    model = StudentPlanSection
    extra = 0
    # inlines = [StudentPlanFileInLine,]

class StudentPlanAdmin(admin.ModelAdmin):

    inlines = [
        StudentPlanSectionInLine,
    ]

    class Meta:
        model = StudentPlan

    list_display = ('plan_title', 'plan_created',)
    list_filter = ('plan_title', 'plan_created',)
    # ordering = ()

admin.site.register(StudentPlan, StudentPlanAdmin)

