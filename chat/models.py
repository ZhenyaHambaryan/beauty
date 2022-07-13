from django.db import models
from userdetails.models import UserDetail
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class ChatRoom(models.Model):
      with_admin = models.BooleanField(default=True)
      created_at = models.DateTimeField(auto_now_add=True)
      is_file = models.BooleanField(default=False)
      last_message = models.TextField(max_length=5000, blank=True, null=True)
      last_message_date = models.DateTimeField(blank=True, null=True)

class ChatMember(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=True, blank=True, 
                                    related_name="user_rooms")
      room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name="room_members")

class ChatMessage(models.Model):
      room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True, 
                                    related_name="messages")
      sender = models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=True, blank=True)
      text = models.TextField(max_length=5000, blank=True, null=True)
      replier_is_admin = models.BooleanField(default=False)
      is_seen = models.BooleanField(default=True)
      file_url = models.CharField(max_length=2500, blank=True, null=True)
      file_type = models.CharField(max_length=255, blank=True, null=True)
      created_at = models.DateTimeField(auto_now_add=True)
      is_deleted = models.BooleanField(default=False)
      parent_message = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)

      def __str__(self):
            return self.text
      
@receiver(post_save, sender=ChatMessage)
def notification_saved_handler(sender, instance, **kwargs):
      room = ChatRoom.objects.get(id=instance.room.id)
      room.is_file = instance.file_url is not None and instance.file_url!=""
      room.last_message = instance.text
      room.last_message_date = instance.created_at
      room.save()
      