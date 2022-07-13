from utils.serializers import ServiceSerializer
from .models import HashTag, Post, PostHashTag, PostLike,PostComment,PostFiles, ReportPost, Review
from rest_framework import serializers
from userdetails.serializers import UserDetailSerializer, UserSmallSerializer

class HashTagSerializer(serializers.ModelSerializer):
      class Meta:
            model = HashTag
            fields = "__all__"

class PostHashTagSerializer(serializers.ModelSerializer):
      hash_tag_details = HashTagSerializer(source='hash_tag',read_only=True)
      class Meta:
            model = PostHashTag
            fields = ('id','hash_tag_details')

class PostSerializer(serializers.ModelSerializer):
      user_details = UserSmallSerializer(source='user',read_only=True)
      hash_tag_posts = PostHashTagSerializer(read_only=True,many=True)
      liked_by_me = serializers.BooleanField(read_only=False, required=False)

      class Meta:
            model = Post
            fields = ['id','user','user_details','text','status','created_at','hash_tag_posts','service','liked_by_me']

      def to_representation(self, instance):
            data = super().to_representation(instance)
            data['comment_count'] = instance.post_comment.count()
            data['like_count'] = instance.post_like.count()
            data['seen_count'] = instance.post_seen.count()
            data['files'] = PostFilesSerializer(instance.post_files,many=True).data
            data['service_details'] = ServiceSerializer(instance.service).data
            return data

class PostOnlyFileSerializer(serializers.ModelSerializer):
      class Meta:
            model = Post
            fields = ["id"]
      
      def to_representation(self, instance):
            data = super().to_representation(instance)
            images = instance.post_files.filter(is_main=True)
            if images is not None:
                  for img in images[0:1]:
                        data['file'] = img.file_url
                        data['file_type'] = img.file_type
            else:
                  data['file']=""
                  data['file_type']=""
            return data

class PostLikeSerializer(serializers.ModelSerializer):
      class Meta:
            model = PostLike
            fields = "__all__"

class PostChildCommentSerializer(serializers.ModelSerializer):
      user_details = UserSmallSerializer(source='user',read_only=True)
      class Meta:
            model = PostComment
            fields = ["id","post","comment","parent","created_at","user","user_details","status"]
       
class PostCommentSerializer(serializers.ModelSerializer):
      user_details = UserSmallSerializer(source='user',read_only=True)
      class Meta:
            model = PostComment
            fields = ["id","comment","created_at","user","user_details","status","post","parent"]

      def to_representation(self, instance):
            data = super().to_representation(instance)
            data['child_comments'] = PostChildCommentSerializer(instance.child_comments.order_by('-id'),
                                                                  many=True).data
            return data 

class PostFilesSerializer(serializers.ModelSerializer):
      class Meta:
            model = PostFiles
            fields = ('file_url','file_type','is_main')

class ReviewSerializer(serializers.ModelSerializer):
      from_user_details = UserDetailSerializer(source='from_user',read_only=True)
      to_user_details = UserDetailSerializer(source='to_user',read_only=True)
      
      class Meta:
            model = Review
            fields = ["id",
                        "from_user",
                        "from_user_details",
                        "to_user_details",
                        "to_user",
                        "comment",
                        "parent",
                        "rating",
                        "created_at",
                        "status",
                        "order"
                  ]
      def to_representation(self, instance):
            data = super().to_representation(instance)
            data['service'] = ServiceSerializer(instance.order.service).data
            try:
                  data['parent_comment_text'] = instance.child.first().comment
            except:
                  data['parent_comment_text'] = ""
            return data 
      
class HashTagSerializer(serializers.ModelSerializer):
      class Meta:
            model = HashTag
            fields = "__all__"

class ReportPostSerializer(serializers.ModelSerializer):
      user_details = UserSmallSerializer(source='user',read_only=True)
      post_details = PostSerializer(source="post",read_only=True)
      class Meta:
            model = ReportPost
            fields = ["id","post","post_details","text","created_at","user","user_details","is_seen"]
      