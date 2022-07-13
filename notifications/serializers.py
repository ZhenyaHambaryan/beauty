from rest_framework import serializers
from .models import (EmailTypes, Notification, NotificationType, ScheduledEmail, ScheduledNotification)

class ScheduledEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledEmail
        fields = "__all__"

class ScheduledNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledNotification
        fields = "__all__"

class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id",'created_at','is_seen','date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_scheduled'] = instance.scheduled_notif is not None
        if instance.notification_type and instance.notification_type.code == "SCHN":
            data['text_en'] = instance.scheduled_notif.text_en
            data['text_fr'] = instance.scheduled_notif.text_fr
        else:
            try:
                data['text_en'] = instance.notification_type.text_en
                data['text_fr'] = instance.notification_type.text_fr
            except:
                data['text_en'] = ""
                data['text_fr'] = ""
        try:
            if str(instance.fullname_user.user.first_name).strip()=="" and str(instance.fullname_user.user.last_name).strip()=="":
                data['username'] = instance.fullname_user.user.username
            else:
                data['username'] = instance.fullname_user.user.first_name+" "+instance.fullname_user.user.last_name
            data['image'] = instance.fullname_user.image
        except:
            data['username'] = ""
            data['image'] = ""
        try:
            data['service_en'] = instance.service.name_en
            data['service_fr'] = instance.service.name_fr
        except:
            data['service_en'] = ""
            data['service_fr'] = ""
        
        return data

class EmailTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTypes
        fields = "__all__"
