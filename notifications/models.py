from django.db import models
from django.db.models.deletion import CASCADE, PROTECT, SET_NULL
from django.db.models.fields import PositiveIntegerField
from utils.models import Service
from userdetails. models import UserDetail
from schedule.models import Order

class ScheduledNotification(models.Model):
      execute_date = models.DateTimeField(null=False, blank=False)
      create_date = models.DateTimeField(auto_now_add=True)
      name = models.CharField(null=True, blank=True,max_length=255)
      text_en = models.CharField(max_length=1000, null=False, blank=False, default="")
      text_fr = models.CharField(max_length=1000, null=False, blank=False, default="")
      done = models.BooleanField(default=False)
      for_users = PositiveIntegerField(null=False,blank=False)
      #1 for all users, 2 only for masters, 3 only for client
      def __str__(self):
            return str(self.text)

class ScheduledEmail(models.Model):
      execute_date = models.DateTimeField(null=False, blank=False)
      create_date = models.DateTimeField(auto_now_add=True)
      name = models.CharField(null=True, blank=True,max_length=255)
      subject_en = models.CharField(null=False, blank=False,max_length=255)
      subject_fr = models.CharField(null=False, blank=False,max_length=255)
      text_en = models.TextField(null=False, blank=False, default="")
      text_fr = models.TextField(null=False, blank=False, default="")
      for_users = PositiveIntegerField(null=False,blank=False)
      done = models.BooleanField(default=False)
      #1 for all users, 2 only for masters, 3 only for client

      def __str__(self):
            return str(self.text)

class NotificationType(models.Model):
      code =  models.CharField(null=False, blank=False,max_length=15)
      text_example = models.TextField(null=True, blank=True, default="")
      text_en = models.TextField(null=False, blank=False, default="")
      text_fr = models.TextField(null=False, blank=False, default="")

      def __str__(self):
            return str(self.code)

class EmailTypes(models.Model):
      code =  models.CharField(null=False, blank=False,max_length=10)
      subject_example = models.TextField(null=True, blank=True, default="")
      text_example = models.TextField(null=True, blank=True, default="")
      subject_en = models.CharField(null=False, blank=False,max_length=255, default="")
      subject_fr = models.CharField(null=False, blank=False,max_length=255, default="")
      text_en = models.TextField(null=False, blank=False, default="")
      text_fr = models.TextField(null=False, blank=False, default="")

      def __str__(self):
            return str(self.code)

class Notification(models.Model):
      notification_type = models.ForeignKey(NotificationType, on_delete=PROTECT, null=False, blank=False)
      service = models.ForeignKey(Service, on_delete=PROTECT, null=True, blank=True)
      owner = models.ForeignKey(UserDetail, related_name="user_notifications",null=False, 
                                                blank=False, on_delete=CASCADE)
      fullname_user =  models.ForeignKey(UserDetail,null=True, blank=True, on_delete=SET_NULL)
      date = models.DateTimeField(null=True, blank=True)
      created_at = models.DateTimeField(auto_now_add=True)
      scheduled_notif = models.ForeignKey(ScheduledNotification, related_name="sch_notifs",null=True, 
                                                blank=True, on_delete=CASCADE)
      is_seen=models.BooleanField(default=False)

      def __str__(self):
            return str(self.notification_type.text_en)
            
class ScheduledPushNotification(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False,
                              related_name="user_scheduled_notifications")
      order = models.ForeignKey(Order, on_delete=CASCADE,null=False, blank=False)
      done = models.BooleanField(default=False)
      notification_type = models.ForeignKey(NotificationType, on_delete=PROTECT, null=False, blank=False)
      service = models.ForeignKey(Service, on_delete=PROTECT, null=True, blank=True)
      fullname_user =  models.ForeignKey(UserDetail,null=True, blank=True, on_delete=SET_NULL)
      created_at = models.DateTimeField(auto_now_add=True)
      date = models.DateTimeField(null=False)

class PushToken(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False,
                              related_name="push_tokens")
      token = models.CharField(null=False, blank=False, max_length=500)
