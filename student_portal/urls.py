from django.conf.urls import include, patterns, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token,refresh_jwt_token, verify_jwt_token
from student_portal.views import IndexView
from forum.views import CategoryViewSet, TopicViewSet, MessageViewSet
from schedule.views import CourseViewSet, CourseScheduleViewSet, RemoveCourseScheduleViewSet
from users.views import LoginView, LogoutView, UserViewSet, SimpleUserViewSet, UserLeaderBoardViewSet, LocationViewSet, StudentNoteViewSet, StudentGoalsViewSet, StudentPracticeLogViewSet, StudentObjectiveViewSet, StudentWishListViewSet, StudentMaterialsViewSet, StudentPlanViewSet, StudentPlanSectionViewSet, StudentPlanFileViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'users-simple', SimpleUserViewSet)
router.register(r'users-leaderboard', UserLeaderBoardViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'student-notes', StudentNoteViewSet)
router.register(r'student-goals', StudentGoalsViewSet)
router.register(r'student-practice-logs', StudentPracticeLogViewSet)
router.register(r'student-objectives', StudentObjectiveViewSet)
router.register(r'student-wish-list', StudentWishListViewSet)
router.register(r'student-materials', StudentMaterialsViewSet)
router.register(r'student-plan', StudentPlanViewSet)
router.register(r'student-plan-section', StudentPlanSectionViewSet)
router.register(r'student-plan-file', StudentPlanFileViewSet)
router.register(r'forum-category', CategoryViewSet)
router.register(r'forum-topics', TopicViewSet)
router.register(r'forum-message', MessageViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'course-schedule', CourseScheduleViewSet)
router.register(r'course-schedule-remove', RemoveCourseScheduleViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include(router.urls)),

    url(r'^$',  IndexView.as_view(), name='index'),

    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),

    url(r'^api/v1/auth/token/', obtain_jwt_token),
    url(r'^api/v1/auth/refresh/', refresh_jwt_token),
    url(r'^api/v1/auth/verify/', verify_jwt_token),

    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', views.password_reset_complete, name='password_reset_complete'),
]