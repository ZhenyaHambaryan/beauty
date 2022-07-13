from userdetails.models import UserDetail
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import  post_save
from notifications.views import send_notification
from utils.models import Service

class HashTag(models.Model):
      text = models.CharField(max_length=255)

      def __str__(self):
            return self.text

class Post(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE,related_name="user_posts")
      text = models.TextField(null=True,blank=True)
      status = models.CharField(null=False, default="accepted",max_length=255)
      service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.PROTECT)
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.text

class PostHashTag(models.Model):
      hash_tag = models.ForeignKey(HashTag, on_delete=models.CASCADE,related_name="post_hash_tags")
      post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="hash_tag_posts")

class PostFiles(models.Model):
      post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_files")
      file_url = models.TextField(null=False,blank=False)
      file_type = models.CharField(null=False,blank=False,max_length=500)
      is_main = models.BooleanField(default=False)
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.text

class PostLike(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
      post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_like")
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.post.text
      class Meta:
            unique_together = ('user', 'post')

class HidePost(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="user_hide_posts")
      post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_hide")
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.post.text
      class Meta:
            unique_together = ('user', 'post')

class PostSeen(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
      post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_seen")
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.post.text
      class Meta:
            unique_together = ('user', 'post')

class PostComment(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
      post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_comment")
      comment = models.TextField(null=True,blank=True)
      parent = models.ForeignKey('self', on_delete=models.CASCADE,related_name="child_comments", 
                                    null=True,blank=True)
      status = models.CharField(null=False, default="accepted",max_length=255)
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.comment

class Review(models.Model):
      parent = models.ForeignKey("self",on_delete=models.CASCADE,null=True, blank=True, related_name="child")
      from_user = models.ForeignKey(UserDetail, on_delete=models.CASCADE,related_name="written_reviews")
      to_user = models.ForeignKey(UserDetail, on_delete=models.CASCADE,related_name="my_reviews")
      comment = models.TextField(null=True,blank=True)
      rating = models.PositiveIntegerField(default=None,null=False,blank=False)
      status = models.CharField(null=False, default="accepted",max_length=255)
      order = models.ForeignKey('schedule.Order', on_delete=models.SET_NULL,null=True,blank=True,
                                    related_name="order_reviews")
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.comment

class ReportPost(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="user_reported_posts")
      text = models.TextField(null=True, blank=True)
      post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_report")
      is_seen = models.BooleanField(default=False)
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.post.text

@receiver(post_save, sender=Review)
def pre_save_review(sender, instance=None, created=False, **kwargs):
      if created:
            if instance.to_user.user_role.code == "CL" and instance.order.master_id==instance.to_user_id:
                  type="RM"
            else:
                  type="RC"
            send_notification(type,owner=instance.to_user_id,fullname_user=instance.from_user_id,
                        service=instance.order.service_id)

@receiver(post_save, sender=ReportPost)
def hide_post_for_user(sender, instance=None, created=False, **kwargs):
      if created:
            hide_post = HidePost(post_id=instance.post_id,user_id=instance.user_id)
            hide_post.save()

