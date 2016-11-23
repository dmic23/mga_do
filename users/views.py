# -*- coding: utf-8 -*-
import json
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from users.models import User, Location, StudentNote, StudentGoal, StudentPracticeLog, StudentObjective, StudentWishList, StudentMaterial, StudentPlan, StudentPlanSection, StudentPlanFile
from users.serializers import UserSerializer, LocationSerializer, StudentNoteSerializer, StudentGoalSerializer, StudentPracticeLogSerializer, StudentObjectiveSerializer, StudentWishListSerializer, StudentMaterialSerializer, StudentPlanSerializer, StudentPlanSectionSerializer, StudentPlanFileSerializer
from users.tasks import send_basic_email


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(user=self.request.user, **self.request.data)
        else:
            return Response({
                'status': 'Bad request',
                'message': 'Account could not be created with received data.'
            }, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        if serializer.is_valid():
            temp_file = self.request.data.pop('user_pic')
            file_dict = {}
            for i in self.request.data:
                if i != 'user_pic': 
                    item = self.request.data[i]
                    file_dict[i] = item
            for f in temp_file:
                file_dict['user_pic'] = f

            serializer.save(user=self.request.user, **file_dict)

class LocationViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)  


class StudentNoteViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentNote.objects.all()
    serializer_class = StudentNoteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_create(self, serializer):
        if serializer.is_valid():
            student_id = self.request.data.pop('student')
            student = User.objects.get(id=student_id)
            serializer.save(student=student, note_created_by=self.request.user, **self.request.data)
  
    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(note_updated_by=self.request.user, **self.request.data)


class StudentGoalsViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentGoal.objects.all()
    serializer_class = StudentGoalSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_create(self, serializer):
        if serializer.is_valid():
            studentId = self.request.data.pop('student')
            student = User.objects.get(id=studentId)
            serializer.save(student=student, goal_created_by=self.request.user, **self.request.data)

    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(goal_updated_by=self.request.user, **self.request.data)


class StudentPracticeLogViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentPracticeLog.objects.all()
    serializer_class = StudentPracticeLogSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, )

    def perform_create(self, serializer):
        if serializer.is_valid():
            studentId = self.request.data.pop('student')
            student = User.objects.get(id=studentId)
            serializer.save(student=student, practice_item_created_by=self.request.user, **self.request.data)

    def perform_update(self, serializer):
        if serializer.is_valid():
            studentId = self.request.data.pop('student')
            serializer.save(practice_item_updated_by=self.request.user, **self.request.data)


class StudentObjectiveViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentObjective.objects.all()
    serializer_class = StudentObjectiveSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_create(self, serializer):
        if serializer.is_valid():
            studentId = self.request.data.pop('student')
            student = User.objects.get(id=studentId)
            send_basic_email.delay(student.id, 'UPD')
            serializer.save(student=student, objective_created_by=self.request.user, **self.request.data)

    def perform_update(self, serializer):
        if serializer.is_valid():
            objective = StudentObjective.objects.get(id=self.request.data['id'])
            send_basic_email.delay(objective.student.id, 'UPD')
            serializer.save(objective_updated_by=self.request.user, **self.request.data)


class StudentWishListViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentWishList.objects.all()
    serializer_class = StudentWishListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, )

    def perform_create(self, serializer):
        if serializer.is_valid():
            studentId = self.request.data.pop('student')
            student = User.objects.get(id=studentId)
            serializer.save(student=student, wish_item_created_by=self.request.user, **self.request.data)

    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(wish_item_updated_by=self.request.user, **self.request.data)


class StudentMaterialsViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentMaterial.objects.all()
    serializer_class = StudentMaterialSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_create(self, serializer):
        if serializer.is_valid():
            if 'file' in self.request.data:
                temp_file = self.request.data.pop('file')

            file_dict = {}
            group = []
            for k, v in self.request.data.iteritems():
                if 'group_student' in k:
                    group.append(v)

                if k != 'file' and 'group_student' not in k:
                    item = self.request.data.get(k)
                    file_dict[k] = item

            file_dict['material_added_by'] = self.request.user

            for f in temp_file:
                file_dict['file'] = f

            student_id = file_dict.pop('student')
            student = User.objects.get(id=student_id)
            serializer.save(student=student, group=group, **file_dict)

    def perform_update(self, serializer):
        if serializer.is_valid():
            file_dict = {}
            group = []
            if 'file' in self.request.data:
                temp_file = self.request.data.pop('file')
                for f in temp_file:
                    file_dict['file'] = f

            for k, v in self.request.data.iteritems():
                if 'group_student' in k:
                    group.append(v)

                if k != 'file' and 'group_student' not in k: 
                    item = self.request.data.get(k)
                    file_dict[k] = item

            file_dict['material_updated_by'] = self.request.user

            serializer.save(group=group, **file_dict)


class StudentPlanViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentPlan.objects.all()
    serializer_class = StudentPlanSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, id=None):
        if self.request.user.is_admin:
            queryset = StudentPlan.objects.all()
        else:
            queryset = StudentPlan.objects.filter(student=self.request.user)
        serializer = StudentPlanSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if serializer.is_valid():
            user = self.request.user;

            if 'plan_student' in self.request.data:
                students = self.request.data.pop('plan_student')
            else:
                students = None

            serializer.save(plan_student=students, user=user, **self.request.data)

    def perform_update(self, serializer):
        if serializer.is_valid():
            user = self.request.user;

            if 'plan_student' in self.request.data:
                students = self.request.data.pop('plan_student')
            else:
                students = None

            serializer.save(plan_student=students, user=user, **self.request.data)

    def perform_destroy(self, instance):
        try:
            plan_users = User.objects.filter(student_plan=instance)
            if plan_users:
                for user in plan_users:
                    user.student_plan = None
                    user.save()
        except:
            pass

        try:
            instance.delete()
        except:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentPlanSectionViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentPlanSection.objects.all()
    serializer_class = StudentPlanSectionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)       

    def perform_create(self, serializer):
        if serializer.is_valid():
            file_dict = {}
            file_arr = []

            for k, v in self.request.data.iteritems():
                if 'files' in k:
                    file_arr.append(v)

                if 'files' not in k: 
                    item = self.request.data.get(k)
                    file_dict[k] = item

            file_dict['section_created_by'] = self.request.user

            serializer.save(files=file_arr, **file_dict)

    def perform_update(self, serializer):
        if serializer.is_valid():
            file_dict = {}
            file_arr = []

            for k, v in self.request.data.iteritems():
                if 'files' in k:
                    file_arr.append(v)

                if 'files' not in k: 
                    item = self.request.data.get(k)
                    file_dict[k] = item

            file_dict['section_updated_by'] = self.request.user

            serializer.save(files=file_arr, **file_dict) 


class StudentPlanFileViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = StudentPlanFile.objects.all()
    serializer_class = StudentPlanFileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)    


class LoginView(views.APIView):

    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                serialized = UserSerializer(user)
                return Response(serialized.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username or password invalid'
            }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(views.APIView):

    def post(self, request, format=None):
        logout(request)
        return Response({}, status=status.HTTP_204_NO_CONTENT)
