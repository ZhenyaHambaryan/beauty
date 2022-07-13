import email
from userdetails.models import UserDetail
from .models import (EmailTypes, Notification, NotificationType, PushToken, ScheduledEmail, ScheduledNotification, ScheduledPushNotification)
from .serializers import (EmailTypesSerializer, NotificationSerializer, NotificationTypeSerializer, ScheduledEmailSerializer, ScheduledNotificationSerializer)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django_filters import rest_framework as filters
from beauty.settings import FIREBASE_PUSH_KEY 
import requests, json
from django.core.mail import EmailMultiAlternatives
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class ScheduledEmailViewSet(viewsets.ModelViewSet):
      queryset = ScheduledEmail.objects.all().order_by("-id")
      filter_backends = [filters.DjangoFilterBackend,]
      filter_fields = ['for_users','done']
      serializer_class = ScheduledEmailSerializer

class ScheduledNotificationViewSet(viewsets.ModelViewSet):
      queryset = ScheduledNotification.objects.all().order_by("-id")
      filter_backends = [filters.DjangoFilterBackend,]
      filter_fields = ['for_users','done']
      serializer_class = ScheduledNotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
      queryset = Notification.objects.all().order_by("-created_at")
      filter_backends = [filters.DjangoFilterBackend,]
      serializer_class = NotificationSerializer

      def list(self,request,):
            owner = request.GET.get("owner")
            queryset = Notification.objects.filter().order_by("-created_at")
            paginator = PageNumberPagination()
            paginator.page_size =10
            if owner:
                  queryset=queryset.filter(owner_id=owner)
            posts = paginator.paginate_queryset(queryset, request)
            for item in Notification.objects.filter(owner_id=owner,is_seen=False):
                  item.is_seen=True
                  item.save()
            return paginator.get_paginated_response(NotificationSerializer(
                                                      posts,many=True).data)

class NotificationTypeViewSet(viewsets.ModelViewSet):
      queryset = NotificationType.objects.exclude(code="SCHN").exclude(
                                                      code="PUSH_CLIENT").exclude(
                                                      code="PUSH_MASTER")
      serializer_class = NotificationTypeSerializer
      
class EmailTypesViewSet(viewsets.ModelViewSet):
      queryset = EmailTypes.objects.all()
      serializer_class = EmailTypesSerializer

def send_notification(type, owner, date=None, fullname_user=None, service=None,):
      user = UserDetail.objects.get(id=owner)
      notification_type = NotificationType.objects.get(code=type)
      notification = Notification(notification_type=notification_type,
                                    owner_id=owner,
                                    date=date,
                                    fullname_user_id=fullname_user,
                                    service_id=service)
      notification.save()
      lang = "EN"
      langs = user.settings.all()
      for lan in langs:
            lang = lan.language.code
            break
      text = notification_type.text_fr if lang=="FR" else notification_type.text_en
      if notification.service is not None:
            text = text.replace("<<SERVICE<<",notification.service.name_en if lang=="EN" else notification.service.name_fr)
      if notification.fullname_user is not None:

            if str(notification.fullname_user.user.first_name).strip() =="" and str(notification.fullname_user.user.last_name).strip() =="":
                  show_name = str(notification.fullname_user.user.username).strip()
            else:
                  show_name = f"{str(notification.fullname_user.user.first_name).strip()} {str(notification.fullname_user.user.last_name).strip()}"
            text = text.replace("<<USERNAME<<",show_name)
      if langs.count()>0:
            if langs.first().push_notification:
                  for i in user.push_tokens.all():
                        send_push(to=i.token, title="",body=text)   
      else:
            for i in user.push_tokens.all():
                  send_push(to=i.token, title="",body=text)   
      return True

def send_push(to,title,body):
      headers = {
            "Authorization": str("key="+FIREBASE_PUSH_KEY),
            "Content-Type":"application/json; UTF-8"
            }
      data={
            "to": to,
            "notification": {
                  "title": title,
                  "body": body,
                  "sound":"default"
            }
      }
      requests.post("https://fcm.googleapis.com/fcm/send",data = json.dumps(data), headers=headers)
      return True

def send_scheduled_email(subject, to_email, text):
      text_content = 'This is an important message.'
      msg = EmailMultiAlternatives(subject, text_content, '"Beautycils" <contact@beautycils.com>', [to_email])
      msg.attach_alternative(text, "text/html")
      msg.send()

def send_email(to_email, code,service_name=None, user_name=None, 
               lang=None, code_email=None,password=None):
      text_content = 'This is an important message.'
      email_type = EmailTypes.objects.get(code=code)
      subject = email_type.subject_fr if lang =="FR" else email_type.subject_en
      msg = EmailMultiAlternatives(subject, text_content, '"Beautycils" <contact@beautycils.com>', [to_email])
      text = email_type.text_fr if lang =="FR" else email_type.text_en
      text = text.replace("<<SERVICE<<",str(service_name)).replace("<<USERNAME<<",str(user_name)
                              ).replace("<<CODE<<",str(code_email)).replace("<<PASSWORD<<",str(code_email))
      msg.attach_alternative(text, "text/html")
      msg.send()
      
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unseen_notifications_count(request):
      return Response({
                  "count":Notification.objects.filter(owner__user_id=request.user.id,
                                                            is_seen=False).count()
            },status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_push_token(request):
      user = UserDetail.objects.get(user_id=request.user.id)
      if PushToken.objects.filter(user__user_id=user.id, token=request.data['push_token']).count()==0:
            token = PushToken(user_id=user.id, token=request.data['push_token'])
            token.save()
      return Response({"message":"OK"},status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_push_token(request):
      for token in  PushToken.objects.filter(user__user_id=request.user.id,token=request.data['push_token']):
            token.delete()
      return Response({"message":"OK"},status=200)
