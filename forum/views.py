# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions, status, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from forum.models import Category, Topic, Message
from forum.serializers import CategorySerializer, TopicSerializer, MessageSerializer
from users.models import User


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class TopicViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_create(self, serializer):
        if serializer.is_valid():
            user = self.request.user
            cat_id = self.request.data.pop('category_id')
            cat = Category.objects.get(id=cat_id)
            serializer.save(topic_category=cat, topic_created_by=user, **self.request.data)


class MessageViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def perform_create(self, serializer):
        if serializer.is_valid():
            user = self.request.user
            file_dict = {}
            files = []

            for i in self.request.data:
                item = self.request.data[i]
                file_dict[i] = item

            for k,v in file_dict.iteritems():
                if 'message_file' in k:
                    files.append(v)
                if k == 'topic_id':
                    topic_id = v
                if k == 'message':
                    message = v

            topic = Topic.objects.get(id=topic_id)
            serializer.save(message_user=user, message_topic=topic, message=message, files=files)
