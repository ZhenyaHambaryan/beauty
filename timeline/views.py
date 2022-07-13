
from userdetails.models import UserDetail
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import HashTag, HidePost, Post, PostComment, PostHashTag, PostLike, PostFiles, PostSeen, ReportPost, Review
from rest_framework import status
from .serializers import (
      PostSerializer, 
      PostOnlyFileSerializer,
      ReportPostSerializer,
      ReviewSerializer,
      PostCommentSerializer)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination

class PostViewSet(viewsets.ModelViewSet):
      queryset = Post.objects.all().order_by("-id")
      serializer_class = PostSerializer

      def list(self,request,):
            queryset = Post.objects.all().order_by("-id")
            paginator = PageNumberPagination()
            paginator.page_size =10
            user_id = request.GET.get("user_id")
            status = request.GET.get("status")
            hide_hiddens = request.GET.get("hide_hiddens")
            hash_tag_posts__hash_tag__text = request.GET.get("hash_tag_posts__hash_tag__text")
            if user_id is not None and user_id !="":
                  queryset = queryset.filter(user_id=user_id)
            if status is not None and status !="":
                  queryset = queryset.filter(status=status)
            if hide_hiddens is not None and hide_hiddens !="":
                  queryset = queryset.exclude(post_hide__user__user_id=request.user.id)
            if hash_tag_posts__hash_tag__text is not None and hash_tag_posts__hash_tag__text !="":
                  queryset = queryset.filter(hash_tag_posts__hash_tag__text__icontains=hash_tag_posts__hash_tag__text)
            posts = paginator.paginate_queryset(queryset, request)
            result = []
            for item in posts:
                  data = PostSerializer(item).data
                  data['liked_by_me'] = item.post_like.filter(user__user_id=request.user.id).count()>0
                  result.append(data)
            return paginator.get_paginated_response(result)

      def retrieve(self, request, *args, **kwargs):
            post = self.get_object()
            data = PostSerializer(post).data
            try:
                  if request.user is not None:
                        user = UserDetail.objects.get(user_id=request.user.id)
                        if post.post_seen.filter(user=user).count()==0 and user!=post.user:
                              PostSeen(user=user,post=post).save()
            except:
                  pass
            try:
                  data['liked_by_me'] = post.post_like.filter(user__user_id=request.user.id).count()>0
            except:
                  data['liked_by_me']=False
            result = PostSerializer(self.get_object()).data
            try:
                  result['liked_by_me'] = post.post_like.filter(user__user_id=request.user.id).count()>0
            except:
                  result['liked_by_me']=False
            return Response(result, status = status.HTTP_200_OK)

      def create(self, request):
            user = UserDetail.objects.get(user_id=request.user.id)
            post = Post(text = request.data['text'].strip(),
                        user_id = user.id, 
                        service_id=request.data['service'])
            post.save()
            for item in request.data["files"]:
                  PostFiles(post=post, 
                              file_url=item['file_url'], 
                              file_type=get_file_type(item['file_type']), 
                              is_main=item['is_main']).save()
            for item in request.data["hash_tags"]:
                  text = item['text'].lower().strip().replace("#","")
                  try:
                        hash_tag = HashTag.objects.get(text__iexact=text)
                        PostHashTag(post=post, hash_tag=hash_tag).save()
                  except:
                        new_hash_tag = HashTag(text=text)
                        new_hash_tag.save()
                        PostHashTag(post=post, hash_tag_id=new_hash_tag.id).save()
            return Response(PostSerializer(post).data, status = status.HTTP_200_OK)

      def update(self, request, pk=None):
            post = Post.objects.get(id=pk)
            post.text = request.data['text'].strip()
            post.service_id = request.data['service']
            post.save()
            try:
                  PostFiles.objects.filter(post_id=pk).delete()
            finally:
                  for item in request.data["files"]:
                        PostFiles(post=post, 
                                    file_url=item['file_url'], 
                                    file_type=get_file_type(item['file_type']), 
                                    is_main=item['is_main']).save()
            try:
                  PostHashTag.objects.filter(post_id=pk).delete()
            finally:
                  for item in request.data["hash_tags"]:
                        try:
                              hash_tag = HashTag.objects.get(text__iexact=item['text'])
                              PostHashTag(post=post, hash_tag=hash_tag).save()
                        except:
                              hash_tag = HashTag(text=item['text'])
                              hash_tag.save()
                              PostHashTag(post=post, hash_tag=hash_tag).save()       
                  return Response(PostSerializer(post).data, status = status.HTTP_200_OK)

      @action(methods=['POST'], detail=True,url_path='add-view', url_name='add_view')
      def add_view(self, request,pk=None):
            post = Post.objects.get(id=pk)
            if request.user is not None:
                  user = UserDetail.objects.get(user_id=request.user.id)
                  if post.user != user:
                        if post.post_seen.filter(user=user).count()==0:
                              PostSeen(user=user,post=post).save()
            return Response({"message":"OK"})

      @action(methods=['GET'], detail=False,url_path='post-by-radius', url_name='post_by_radius')
      def post_by_radius(self, request,pk=None):   
            radius = request.GET.get("radius")
            long = self.request.query_params.get('long',"2.349014")
            lat = self.request.query_params.get('lat',"48.864716")
            offset = request.GET.get("offset")
            limit = request.GET.get("limit")
            hash_tag = request.GET.get("hash_tag")
            print(request.user.id)
            print("___________________________")
            if request.user.id is not None:
                  
                  user_id = UserDetail.objects.get(user_id=request.user.id).id
            else:
                  user_id=None
            query = """SELECT timeline_post.*, """
            if request.user.id is not None:
                  query+=""" COUNT(timeline_hidepost.id) AS hides_count, 
                              CASE WHEN COUNT(timeline_postlike.id)>0  THEN TRUE ELSE FALSE END AS liked_by_me, """
                              
            else:
                  query+=" 0 as hides_count, FALSE as liked_by_me, "
            query+=""" ( 3959 * ACOS( COS( RADIANS("""+lat+""")) * COS( RADIANS(address_latitude) )
                  * COS( RADIANS(address_longitude) - RADIANS("""+long+""") ) + SIN( RADIANS("""+lat+""") )
                  * SIN(RADIANS(address_latitude)) ) ) AS distance  
                  FROM userdetails_userdetail
                  INNER JOIN auth_user ON auth_user.id = userdetails_userdetail.user_id
                  INNER JOIN timeline_post ON timeline_post.user_id = userdetails_userdetail.id"""
            if request.user.id is not None:
                  query+=""" LEFT JOIN `timeline_hidepost` ON `timeline_hidepost`.post_id=timeline_post.id   
                  AND `timeline_hidepost`.user_id="""+str(user_id)+"""
                  LEFT JOIN `timeline_postlike` ON `timeline_postlike`.`post_id`=timeline_post.id 
                  AND `timeline_postlike`.user_id="""+str(user_id)+""" """

            query+= """ LEFT JOIN `timeline_posthashtag` ON `timeline_posthashtag`.`post_id` = `timeline_post`.`id`
                  LEFT JOIN `timeline_hashtag` ON timeline_hashtag.id=timeline_posthashtag.hash_tag_id"""
            if hash_tag is not None:
                  query+=""" WHERE  timeline_hashtag.text='"""+str(hash_tag)+"""' AND """
            else:
                  query+=" WHERE "
            if request.user.id is not None:
                  query+=""" auth_user.is_active=1  
                        GROUP  BY timeline_post.id
                        HAVING  (distance < """+str(radius)+""" OR timeline_post.user_id="""+str(user_id)+""" 
                        ) AND (hides_count=0) ORDER BY timeline_post.id DESC
                        LIMIT """+str(offset)+""","""+str(limit)+""" """
            else:
                  query+="""  auth_user.is_active=1
                  GROUP BY timeline_post.id 
                  HAVING (distance <"""+str(radius)+""" ) AND (hides_count=0) ORDER BY timeline_post.id DESC
                   LIMIT """+str(offset)+""", """+str(limit)+""""""
            print(query)
            queryset = Post.objects.raw(query) 
            return Response(PostSerializer(queryset,many=True).data,status=200)
             
class PostCommentViewSet(viewsets.ModelViewSet):
      queryset = PostComment.objects.filter(parent=None).order_by('-id')
      serializer_class = PostCommentSerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['post',"status"]
      # permission_classes =[IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
      queryset = Review.objects.all().order_by('-id')
      serializer_class = ReviewSerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['to_user','from_user',"status",'order']
      # permission_classes =[IsAuthenticated]

class ReportPostViewSet(viewsets.ModelViewSet):
      queryset = ReportPost.objects.all().order_by('-id')
      serializer_class = ReportPostSerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['user','post',"is_seen"]
      permission_classes =[IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def like_or_dislike(request,pk):
      user = UserDetail.objects.get(user_id=request.user.id)
      post_like = PostLike.objects.filter(user=user,post_id=pk)
      if post_like.count()>0:
            post_like.delete()
      else:
            PostLike(user=user,post_id=pk).save()
      return Response({"message":"OK","like_count":PostLike.objects.filter(post_id=pk).count()},status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts_only_file(request,pk):
      paginator = PageNumberPagination()
      paginator.page_size =10
      qs = Post.objects.filter(user_id=pk)
      posts = paginator.paginate_queryset(qs, request)
      return paginator.get_paginated_response(PostOnlyFileSerializer(posts, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_to_review(request,pk):
      parent = Review.objects.get(id=pk)
      review  = Review(parent_id=pk, comment=request.data['comment'],
                       order_id = parent.order.id,
                       from_user_id=parent.to_user_id,
                       to_user_id = parent.from_user_id,
                       rating = request.data['rating']
                       )
      review.save()
      return Response(ReviewSerializer(review).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accept_post(request,pk):
      post = Post.objects.get(id=pk)
      post.status = "accepted"
      post.save()
      return Response(PostSerializer(post).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accept_comment(request,pk):
      post_comment = PostComment.objects.get(id=pk)
      post_comment.status = "accepted"
      post_comment.save()
      return Response(PostCommentSerializer(post_comment).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accept_review(request,pk):
      post_review = Review.objects.get(id=pk)
      post_review.status = "accepted"
      post_review.save()
      return Response(ReviewSerializer(post_review).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_post(request,pk):
      post = Post.objects.get(id=pk)
      post.status = "canceled"
      post.save()
      return Response(PostSerializer(post).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_comment(request,pk):
      post_comment = PostComment.objects.get(id=pk)
      post_comment.status = "canceled"
      post_comment.save()
      return Response(PostCommentSerializer(post_comment).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_review(request,pk):
      post_review = Review.objects.get(id=pk)
      post_review.status = "canceled"
      post_review.save()
      return Response(ReviewSerializer(post_review).data,status=200)

def get_file_type(string):
      if string == "image/bmp" or string == "image/gif" or string == "image/vnd.microsoft.icon" \
            or string == "image/jpeg"  or string == "image/png" or string == "image/tiff" \
            or string == "image/webp" or string == "image/svg+xml" or string == "image":
                  return "image"
      elif string == "video/x-msvideo" or string == "video/mp4" or string == "video/mpeg" \
            or string == "video/ogg" or string == "video/mp2t" or string == "video/webm" \
            or string == "video/3gpp2" or string == "video/3gpp" or string == "video":
                  return "video"
      else:
            return ""

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hide_post(request,pk):
      try:
            user_detail = UserDetail.objects.get(user_id = request.user.id)
            HidePost(user_id = user_detail.id, post_id = pk).save()
            return Response({"message":"succeed"},status=200)
      except:
            return Response({"message":"already hidden"},status=400)

