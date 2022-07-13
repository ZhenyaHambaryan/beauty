import  datetime
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from userdetails.models import UserDetail, MasterService
from rest_framework.decorators import api_view, permission_classes
from timeline.models import Post, PostComment
from schedule.models import Order

def date_format(date):
      return datetime.datetime.strptime(date, '%Y-%m-%d')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_joined_user(request):
      start_date =date_format(request.data['start_date'])
      end_date =date_format(request.data['end_date'])
      role = request.data['role']
      users = UserDetail.objects.filter(created_at__gte=start_date).filter(
                              created_at__lte=end_date
                        ).filter(user_role__code="CL")
      if role == "CL":
            users=users.filter(is_client=True)
      elif role == "MST":
            users=users.filter(is_master=True)
      dates = set([datetime.datetime.strftime(item.created_at, '%Y-%m-%d') for item in users])
      result = []
      for date in dates:
            result.append({
                  "created_at__date":date,
                  "count":users.filter(created_at__startswith = date).count()
            })
      return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_post(request):
      start_date =date_format(request.data['start_date'])
      end_date =date_format(request.data['end_date'])
      post = Post.objects.filter(created_at__gte=start_date).filter(
                              created_at__lte=end_date
                        ).filter(status="accepted")
      dates = set([datetime.datetime.strftime(item.created_at, '%Y-%m-%d') for item in post])
      result = []
      for date in dates:
            result.append({
                  "created_at__date":date,
                  "count":post.filter(created_at__startswith = date).count()
            })
      return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_post_comment(request):
      start_date =date_format(request.data['start_date'])
      end_date =date_format(request.data['end_date'])
      post_comment = PostComment.objects.filter(created_at__gte=start_date).filter(
                              created_at__lte=end_date
                        ).filter(status="accepted")
      dates = set([datetime.datetime.strftime(item.created_at, '%Y-%m-%d') for item in post_comment])
      result = []
      for date in dates:
            result.append({
                  "created_at__date":date,
                  "count":post_comment.filter(created_at__startswith = date).count()
            })
      return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_order(request):
      start_date =date_format(request.data['start_date'])
      end_date =date_format(request.data['end_date'])
      order = Order.objects.filter(created_at__gte=start_date).filter(
                              created_at__lte=end_date
                        ).filter(status="accepted")           
      dates = set([datetime.datetime.strftime(item.created_at, '%Y-%m-%d') for item in order])
      result = []
      for date in dates:
            result.append({
                  "created_at__date":date,
                  "count":order.filter(created_at__startswith = date).count()
            })
      return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_master_service(request):
      start_date =date_format(request.data['start_date'])
      end_date =date_format(request.data['end_date'])
      master_service = MasterService.objects.filter(created_at__gte=start_date).filter(
                              created_at__lte=end_date
                        )
      dates = set([datetime.datetime.strftime(item.created_at, '%Y-%m-%d') for item in master_service])
      result = []
      for date in dates:
            result.append({
                  "created_at__date":date,
                  "count":master_service.filter(created_at__startswith = date).count()
            })
      return Response(result)
