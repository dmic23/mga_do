# -*- coding: utf-8 -*-
from django.contrib.auth import update_session_auth_hash
from datetime import date
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from forum.models import Category, Topic, Message, MessageFile
from users.serializers import SimpleUserSerializer

class MessageFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = MessageFile
        fields = ('id', 'message', 'message_file', 'message_file_created', 'message_file_created_by',)

class MessageSerializer(serializers.ModelSerializer):
    message_user = SimpleUserSerializer(required=False)
    message_topic = serializers.CharField(required=False)
    file_message = MessageFileSerializer(many=True)

    class Meta:
        model = Message
        fields = ('id', 'message_topic', 'message_user', 'message', 'message_created', 'message_visible', 'file_message',)

    def create(self, validated_data):
        msg_files = validated_data.pop('files')
        file_msg = validated_data.pop('file_message')
        message = Message.objects.create(**validated_data)
        message.save()
        user = validated_data.pop('message_user')
        for file in msg_files:
            msg_file = MessageFile.objects.create(message=message, message_file=file, message_file_created_by=user)
            msg_file.save()
        return message

class TopicSerializer(serializers.ModelSerializer):
    topic_message = MessageSerializer(many=True, required=False)
    topic_category = serializers.CharField(required=False)
    topic_created_by = serializers.CharField(required=False)

    class Meta:
        model = Topic
        fields = ('id', 'topic_category', 'topic', 'topic_created_by', 'topic_created', 'topic_message',)

    def create(self, validated_data):
        user = validated_data.get('topic_created_by')
        if 'message' in validated_data:
            msg = validated_data.pop('message')
        else:
            msg = None

        topic = Topic.objects.create(**validated_data)
        topic.save()

        if msg:
            new_msg = Message.objects.create(message_topic=topic, message_user=user, message=msg)
            new_msg.save()
        return topic


class CategorySerializer(serializers.ModelSerializer):
    category_topic = TopicSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'category', 'category_created', 'category_created_by', 'category_topic',)
