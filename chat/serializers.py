from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ChatMessage, ChatRoom
from userdetails.serializers import UserDetailSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"

class ChatMemberSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    class Meta:
        model = ChatRoom
        fields = "__all__"

class ChatRoomWithMembersSerializer(serializers.ModelSerializer):
    room_members=ChatMemberSerializer(many=True,read_only=True)
    class Meta:
        model = ChatRoom
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["unseen_message_count"] = instance.messages.filter(
                is_seen=False).exclude(sender_id=self.context.get("user_id")).count()
        return data

class ChatMessage1Serializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserDetailSerializer(read_only=True)
    parent_message = ChatMessage1Serializer(read_only=True)
    class Meta:
        model = ChatMessage
        fields = '__all__'
    
