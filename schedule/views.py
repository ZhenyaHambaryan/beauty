from django.db.models.query_utils import Q
from notifications.models import NotificationType, ScheduledPushNotification
from notifications.views import send_email, send_notification, send_push
from schedule.serializers import OrderSerializer, TransactionSerializer
from schedule.models import Order, Transaction
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import stripe, math
from datetime import datetime, timedelta
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from userdetails.models import FavoriteMasters, MasterService, UserDetail
from userdetails.serializers import ClientDetailSerializer, MasterSerializer, MasterService2Serializer
from django.shortcuts import redirect 
from rest_framework.pagination import PageNumberPagination 
from rest_framework.filters import SearchFilter, OrderingFilter 
from beauty.settings import STRIPE_API_KEY 
from django.http import HttpResponsePermanentRedirect
import service
from notifications.views import send_email
from utils.models import General
stripe.api_key = STRIPE_API_KEY

class OrderViewSet(viewsets.ModelViewSet):
      queryset = Order.objects.all().order_by("-id")
      filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
      filter_fields = ['user_id','master_id','service_id','service__category','id','status']
      search_fields = ['service__name_en',"service__name_fr","master__user__first_name",
                        "master__user__last_name","service__category__name_en",     
                                                "service__category__name_fr"]
      permission_classes = [IsAuthenticated]
      serializer_class = OrderSerializer
      ordering_fields = ['start_date', '-start_date','id','-id','created_at','-created_at']

class TransactionViewSet(viewsets.ModelViewSet):
      queryset = Transaction.objects.all().order_by('-id')
      filter_backends = [filters.DjangoFilterBackend, ]
      filter_fields = ['client','master']
      permission_classes = [IsAuthenticated]
      serializer_class = TransactionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_client_orders(request,pk):
      type = request.GET.get("type")
      paginator = PageNumberPagination()
      paginator.page_size = request.GET.get("limit",10)
      queryset = Order.objects.filter(user_id=pk).order_by("-start_date")
      if type=="archived":
            queryset = queryset.filter(Q(status="cancelled") | Q(status="done") | Q(status="passed"))
      elif type == "incomings":
            queryset = queryset.exclude(Q(status="cancelled") | Q(status="done") | Q(status="passed"))
            
      result = paginator.paginate_queryset(queryset, request)
      return paginator.get_paginated_response(
            OrderSerializer(result,many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_master_orders(request):
      type = request.GET.get("type")
      paginator = PageNumberPagination()
      paginator.page_size = request.GET.get("limit",10)
      if type=="archived":
            queryset = Order.objects.filter(Q(master__user_id=request.user.id) & 
                        Q(Q(status="cancelled")|Q(status="done")|Q(status="passed"))).order_by("-start_date")
      elif type == "incomings":
            queryset = Order.objects.filter(master__user_id=request.user.id).exclude(
                        Q(Q(status="cancelled") | Q(status="done") | Q(status="passed")))
      else:
            queryset = Order.objects.filter(master__user_id=request.user.id)
      result = paginator.paginate_queryset(queryset, request)
      return paginator.get_paginated_response(OrderSerializer(result,many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_non_working_date(request):
      date = request.data['date']
      min_date = str(datetime.strptime(date+"T00:00:00",'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = str(datetime.strptime(date+"T00:00:00",'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      events = service.get_events(calendarId=request.data['calendar_id'],
                                    min_date=min_date,
                                    max_date=max_date)
      accepted_orders = []
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['status']=="accepted" \
                  and item['extendedProperties']['private']['event_type']=="order":
                        accepted_orders.append(item)
            except:
                  pass
      if len(accepted_orders) > 0:
            return Response({"message":"There is a accepted order for this day"},status=400)
      else:
            event = {
                  'start': {
                        'dateTime': min_date,
                        'timeZone': 'Europe/London',
                  },
                  'end': {
                        'dateTime': max_date,
                        'timeZone': 'Europe/London',
                  },
                  "extendedProperties": {
                        "private": {
                              "event_type": "non-working"
                        }
                  }
            }
            created_event = service.create_event(body=event,calendar_id=request.data['calendar_id'])
            return Response({"message":created_event},status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_busy_event(request):
      start_time = request.data['start_time']
      end_time = request.data['end_time']
      min_date = str(datetime.strptime(start_time+":00",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = datetime.strptime(end_time+":00",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')+"-00:00"
      accepted_orders = []
      events = service.get_events(calendarId=request.data['calendar_id'],
                                    min_date=min_date,max_date=max_date)
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['status']=="accepted" and item['extendedProperties']['private']['event_type']=="order":
                        accepted_orders.append(item)
            except:
                  pass
      if len(accepted_orders) > 0:
            return Response({"message":"There is a accepted order for this day"},status=400)
      else:
            event = {
                        'start': {
                              'dateTime': min_date,
                              'timeZone': 'Europe/London',
                        },
                        'end': {
                              'dateTime': max_date,
                              'timeZone': 'Europe/London',
                        },
                        "extendedProperties": {
                              "private": {
                                    "event_type": "busy"
                              }
                        }
                  }
            created_event = service.create_event(body=event,calendar_id=request.data['calendar_id'])
            return Response({"message":created_event},status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_working_event(request):
      end_time = str(datetime.strptime(request.data['end_time'],'%Y-%m-%dT%H:%M:%S').strftime('%H:%M:%S'))
      start_day = str(datetime.strptime(request.data['start_time'],'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d'))
      end_date = start_day+"T"+end_time
      recurring_end_date = str(datetime.strptime(request.data['end_time'],'%Y-%m-%dT%H:%M:%S').strftime('%Y%m%dT%H%M%SZ'))
      result = []
      for master_service in request.data['master_services']:
            master_services = {}
            master_services[master_service['id']]=True
            recurrence_type = request.data['recurrence_type']
            if recurrence_type == "daily":
                  recurrence = 'RRULE:FREQ=DAILY;UNTIL='+recurring_end_date
            elif  recurrence_type == "weekly":
                  recurrence = 'RRULE:FREQ=WEEKLY;UNTIL='+recurring_end_date+';BYDAY='+request.data['week_day']
            elif  recurrence_type == "monthly":
                  recurrence = 'RRULE:FREQ=MONTHLY'
            else:
                  recurrence = None
            event = {
                        'start': {
                              'dateTime': request.data['start_time']+'+00:00',
                              'timeZone': 'Europe/London',
                        },
                        'end': {
                              'dateTime': end_date+'+00:00',
                              'timeZone': 'Europe/London',
                        },
                        "extendedProperties": {
                              "private": {
                                    "event_type": "working"
                              },
                              "shared": master_services

                        },
                        'recurrence': [
                              recurrence
                        ],
                  }
            created_event = service.create_event(body=event,calendar_id=request.data['calendar_id'])
            result.append(created_event)
      return Response({"message":result},status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_working_event(request,eid):
      now = datetime.now()
      mdate = now+timedelta(weeks=150)
      min_date = str(now.strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = str(mdate.strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      events = service.get_events(calendarId=request.data['calendar_id'],
                                    min_date=min_date,
                                    max_date=max_date)
      accepted_orders = []
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['status']=="accepted" \
                  and item['extendedProperties']['private']['event_type']=="order":
                        accepted_orders.append(item)
            except:
                  pass
      if len(accepted_orders) > 0:
            return Response({"message":"There is an accepted order after this day"},status=400)
      master_services = {}
      for master_service in request.data['master_services']:
            master_services[master_service['id']]=True
      recurrence_type = request.data['recurrence_type']
      if recurrence_type == "daily":
            recurrence = 'RRULE:FREQ=DAILY'
      elif  recurrence_type == "weekly":
            recurrence = 'RRULE:FREQ=WEEKLY;BYDAY='+request.data['week_day']
      elif  recurrence_type == "monthly":
            recurrence = 'RRULE:FREQ=MONTHLY'
      else:
            recurrence = None
      event = {
                  'start': {
                        'dateTime': request.data['start_time']+'+00:00',
                        'timeZone': 'Europe/London',
                  },
                  'end': {
                        'dateTime': request.data['end_time']+'+00:00',
                        'timeZone': 'Europe/London',
                  },
                  "extendedProperties": {
                        "private": {
                              "event_type": "working"
                        },
                        "shared": master_services

                  },
                  'recurrence': [
                        recurrence
                  ],
            }
      created_event = service.update_event(body=event,calendar_id=request.data['calendar_id'],
                                                      event_id=eid)
      return Response({"message":created_event},status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_working_event(request):
      calendar_id=request.GET.get("calendar_id")
      event_id=request.GET.get("event_id")
      remove_anyway=request.GET.get("remove_anyway",False)
      now = datetime.now()
      mdate = now+timedelta(weeks=150)
      min_date = str(now.strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = str(mdate.strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      events = service.get_events(calendarId=calendar_id,
                                    min_date=min_date,
                                    max_date=max_date)
      accepted_orders = []
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['status']=="accepted" \
                  and item['extendedProperties']['private']['event_type']=="order":
                        accepted_orders.append(item)
            except:
                  pass
      if remove_anyway == False:
            if len(accepted_orders) > 0:
                  return Response({"message":"There is an accepted order after this day"},status=400)
      try: 
            service.delete_event(calendar_id=calendar_id,event_id=event_id)
            return Response({"message":"OK"},status=200)
      except:
            return Response({"message":"error"},status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delete_non_working_day(request):
      date = request.GET.get('date')
      calendar_id = request.GET.get('calendar_id')
      min_date = str(datetime.strptime(date+" 00:00:00",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = str(datetime.strptime(date+" 23:59:59",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      events = service.get_events(calendarId=calendar_id,
                                    min_date=min_date,
                                    max_date=max_date)
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['event_type']=="non-working":
                        service.delete_event(calendar_id=calendar_id,event_id=item['id'])  
            except:
                  pass
      return Response({"message":"OK"},status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
      start_time = request.data['start_time']
      end_time = request.data['end_time']
      min_date = str(datetime.strptime(start_time+":00",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = str(datetime.strptime(end_time+":00",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      count = Order.objects.filter(service_id=request.data['service_id'], user__user_id = request.user.id
                                    ).exclude(Q(status="cancelled") | Q(status="done") | Q(status="passed")).count()
      if count > 0:
            return Response({"message":"You have ordered same service which has no final status."},status = 400)
      working_days = []
      events = service.get_events(calendarId=request.data['calendar_id'],
                                    min_date=min_date,
                                    max_date=max_date)
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['event_type']=="working" \
                        and (item['extendedProperties']['shared'][str(request.data['service_id'])]==True\
                        or item['extendedProperties']['shared'][str(request.data['service_id'])]=="true"\
                        or item['extendedProperties']['shared'][str(request.data['service_id'])]=="True"):
                        working_days.append(item)
            except:
                  pass
      if len(working_days)>0:
            accepted_orders = []
            for item in events['items']:
                  try:
                        if ((item['extendedProperties']['private']['event_type']=="order"
                        and item['extendedProperties']['private']['status']=="accepted" )
                        or item['extendedProperties']['private']['event_type']=="busy"
                        or  item['extendedProperties']['private']['event_type']=="non-working"):
                              accepted_orders.append(item)
                  except:
                        pass
            if len(accepted_orders)>0:
                  return Response({"message":"You can not create order for this date range"},status=400)
            else:
                  event={
                              'start': {
                                    'dateTime': min_date,
                                    'timeZone': 'Europe/London',
                              },
                              'end': {
                                    'dateTime': max_date,
                                    'timeZone': 'Europe/London',
                              },
                              "extendedProperties": {
                                    "private": {
                                          "event_type": "order",
                                          "status":"accepted"
                                    }
                              }
                        }
                  created_event = service.create_event(body=event,calendar_id=request.data['calendar_id'])
                  master_service = MasterService.objects.get(service_id=request.data['service_id'],
                                                                  user_id = request.data['master_id'])
                  if master_service.prepay_percent>0:
                        prepayed_price = round(float(master_service.price+(
                              0 if not master_service.go_home else master_service.go_home_price))*master_service.prepay_percent/100,2)
                        transaction = Transaction(amount=prepayed_price,
                                                      payment_id="some key",
                                                      status="pending",
                                                      client_id=request.data['user_id'],
                                                      master_id = request.data['master_id'],)
                        transaction.save()
                        is_prepayed = True
                        prepayed_status = "pending"
                  else:
                        is_prepayed = False
                        prepayed_price = 0
                        prepayed_status = "no_prepayment"
                  order = Order(user_id=request.data['user_id'],
                                    master_id = request.data['master_id'],
                                    service_id = request.data['service_id'],
                                    status="accepted",
                                    go_home = request.data['go_home'],
                                    minutes=request.data['minutes'],
                                    price=request.data['price'],
                                    start_date=start_time,
                                    end_date=end_time,
                                    comment=request.data['comment'],
                                    google_calendar_id=request.data['calendar_id'],
                                    google_event_id = created_event['id'],
                                    is_prepayed=is_prepayed,
                                    prepayed_price=prepayed_price,
                                    prepayed_status=prepayed_status
                                    )
                  order.save()
                  try:
                        FavoriteMasters.objects.get(user_id = request.data['user_id'],master_id = request.data['master_id'])
                  except:
                        FavoriteMasters(user_id = request.data['user_id'],master_id = request.data['master_id']).save()
                  if is_prepayed:
                        transaction.order = order
                        transaction.save()
                        obj = pay_stripe(request=request,transaction=transaction,price=prepayed_price)
                        transaction.payment_id = obj['id']
                        transaction.save()

                        if obj['status'] == "succeeded":
                              return Response({
                                    "redirect_url":str(obj['id'])+"/"+str(transaction.id),
                                    "do_recirection":True
                                    })
                        else:
                              return Response({"iframe_url":obj['next_action']['redirect_to_url']['url']},status=200)
                  else:
                        try:
                              send_notification("NRS",owner=request.data['master_id'],
                                                      date=min_date,
                                                      fullname_user=request.data['user_id'],
                                                      service=request.data['service_id'])
                        except:
                              pass
                        if order.master.user.email is not None and order.master.user.email !="":
                              lang = "EN"
                              if order.master.settings.all().count()>0:
                                    lang = order.master.settings.all().first().language.code
                              send_email(to_email=order.master.user.email,
                                    code="NEWOM",
                                    service_name=order.service.name_fr if lang == "FR" else order.service.name_en,
                                    lang=lang)
                        ScheduledPushNotification(
                              user_id = request.data['master_id'],
                              order_id=order.id,
                              notification_type_id=NotificationType.objects.get(code="PUSH_MASTER").id,
                              fullname_user_id = request.data['user_id'],
                              service_id = request.data['service_id'],
                              date = datetime.strptime(start_time,'%Y-%m-%d %H:%M')-timedelta(days=1),
                        ).save()
                        if order.user.user.email is not None and order.user.user.email !="":
                              lang = "EN"
                              if order.user.settings.all().count()>0:
                                    lang = order.user.settings.all().first().language.code
                              send_email(to_email=order.user.user.email,
                                    code="NEWOC",
                                    service_name=order.service.name_fr if lang == "FR" else order.service.name_en,
                                    lang=lang)

                        ScheduledPushNotification(
                              user_id = request.data['user_id'],
                              order_id=order.id,
                              notification_type_id=NotificationType.objects.get(code="PUSH_CLIENT").id,
                              fullname_user_id = request.data['master_id'],
                              service_id = request.data['service_id'],
                              date = datetime.strptime(start_time,'%Y-%m-%d %H:%M')-timedelta(days=1),
                        ).save()
                        return Response({"message":"OK"})
      else:
            return Response({"message":"Master is not working in that day for that service."},status=400)

@api_view(['GET'])
def check_payment(request, id, pk):
      transaction = Transaction.objects.get(id=pk)
      order = Order.objects.get(id=transaction.order_id)
      if stripe.PaymentIntent.retrieve(id)['status'] == "succeeded":
            order.prepayed_status = "succeed"
            order.status = "accepted"
            order.save()
            transaction.status="succeed"
            transaction.save()
            event = service.get_event(calendar_id=order.google_calendar_id,
                                          event_id=order.google_event_id)
            event["extendedProperties"]['private']['status'] ="accepted"
            service.update_event(calendar_id=order.google_calendar_id, 
                                    event_id=order.google_event_id, 
                                    body=event)
            send_notification("NRS",owner=order.master_id,
                              date=event["start"]['dateTime'],
                              fullname_user=order.user_id,
                              service=order.service_id)
            if order.master.user.email is not None and order.master.user.email !="":
                  lang = "EN"
                  if order.master.settings.all().count()>0:
                        lang = order.master.settings.all().first().language.code
                  send_email(to_email=order.master.user.email,
                        code="NEWOM",
                        service_name=order.service.name_fr if lang == "FR" else order.service.name_en,
                        lang=lang)
            ScheduledPushNotification(
                                    user_id = order.master_id,
                                    order_id=order.id,
                                    notification_type_id=NotificationType.objects.get(code="PUSH_MASTER").id,
                                    fullname_user_id = order.user.id,
                                    service_id = order.service_id,
                                    date =datetime.strptime(event["start"]['dateTime'],'%Y-%m-%dT%H:%M:%SZ')-timedelta(days=1),
                              ).save()
            if order.user.user.email is not None and order.user.user.email !="":
                  lang = "EN"
                  if order.user.settings.all().count()>0:
                        lang = order.user.settings.all().first().language.code
                  send_email(to_email=order.user.user.email,
                        code="NEWOC",
                        service_name=order.service.name_fr if lang == "FR" else order.service.name_en,
                        lang=lang)
            ScheduledPushNotification( 
                  user_id = order.user.id,
                  order_id=order.id,
                  notification_type_id=NotificationType.objects.get(code="PUSH_CLIENT").id,
                  fullname_user_id = order.master_id,
                  service_id = order.service_id,
                  date = datetime.strptime(event["start"]['dateTime'],'%Y-%m-%dT%H:%M:%SZ')-timedelta(days=1),
            ).save()
            try:
                  FavoriteMasters.objects.get(user_id =order.user.id,master_id = order.master.id)
            except:
                  FavoriteMasters(user_id =order.user.id,master_id = order.master.id).save()
            
            if request.GET.get("rurl") is not None:
                  return CustomRedirect(request.GET.get("rurl")+"?status=succeed")
            else:
                  return Response({"ok":True},status=200)
      else:
            event = service.get_event(calendar_id=order.google_calendar_id,event_id=order.google_event_id)
            event["extendedProperties"]['private']['status'] ="failed"
            service.update_event(calendar_id=order.google_calendar_id, 
                                    event_id=order.google_event_id, 
                                    body=event)
            transaction.delete()
            order.delete()
            if request.GET.get("rurl") is not None:
                  return CustomRedirect(request.GET.get("rurl")+"?status=failed")
            else:
                  return Response({"ok":False},status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request,pk):
      order = Order.objects.get(id=pk)
      if UserDetail.objects.get(user_id = request.user.id).id == order.master_id:
            transactions = Transaction.objects.filter(order_id = pk)
            for transaction in transactions:
                  try:
                        stripe.Refund.create(payment_intent=transaction.payment_id)
                  except:
                        pass
                  transaction.status='refunded'
                  transaction.save()
            if order.user.user.email is not None and order.user.user.email !="":
                  lang = "EN"
                  if order.user.settings.all().count()>0:
                        lang = order.user.settings.all().first().language.code

                  send_email(to_email=order.user.user.email,
                        code="CNCO",
                        service_name=order.service.name_fr if lang == "FR" else order.service.name_en,
                        lang=lang
                        )
            send_notification("COM",owner=order.user_id,
                                    fullname_user=order.master_id,
                                    service=order.service_id)
      else:
            if order.master.user.email is not None and order.master.user.email !="":
                  lang = "EN"
                  if order.master.settings.all().count()>0:
                        lang = order.master.settings.all().first().language.code
                  send_email(to_email=order.user.user.email,
                        code="CNCO",
                        service_name=order.service.name_fr if lang == "FR" else order.service.name_en,
                        lang=lang
                        )
            send_notification("COC",owner=order.master_id,
                                    fullname_user=order.user_id,
                                    service=order.service_id)
      order.status="cancelled"
      try:
            order.cancel_reason = request.data['cancel_reason']
      except:
            pass
      order.save()
      event = service.get_event(calendar_id=order.google_calendar_id,event_id=order.google_event_id)
      event["extendedProperties"]['private']['status'] ="cancelled"
      service.update_event(calendar_id=order.google_calendar_id, 
                              event_id=order.google_event_id, 
                              body=event)
      ScheduledPushNotification.objects.filter(order_id = pk).delete()
      return Response(OrderSerializer(order).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def done_order(request,pk):
      order = Order.objects.get(id=pk)
      order.status="done"
      order.save()
      send_done_push(order_id=order.id)
      return Response({"message":"OK"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_order_count(request,pk):
      order = Order.objects.get(id=pk)
      order_event = service.get_event(calendar_id=order.google_calendar_id,event_id=order.google_event_id)
      min_date = order_event['start']['dateTime']
      max_date = order_event['end']['dateTime']
      events = service.get_events(calendarId=order.google_calendar_id,min_date=min_date,max_date=max_date)
      accepted_orders = []

      for item in events['items']:
            try:
                  if ((item['extendedProperties']['private']['status']=="accepted" 
                  and item['extendedProperties']['private']['event_type']=="order")
                  or item['extendedProperties']['private']['event_type']=="busy"
                  or item['extendedProperties']['private']['event_type']=="non-working"):
                        accepted_orders.append(item)
            except:
                  pass
      if len(accepted_orders)>0:
            return Response({"message":"You can not accept this order with this date."},status=400)
      return Response({"count":Order.objects.filter(start_date=order.start_date, 
                                                master_id=order.master.id,
                                                status="pending").count()},status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accept_order(request,pk):
      order = Order.objects.get(id=pk)
      has_automated_cancelation = request.GET.get("has_automated_cancelation",None)
      order_event = service.get_event(calendar_id=order.google_calendar_id,event_id=order.google_event_id)
      min_date = order_event['start']['dateTime']
      max_date = order_event['end']['dateTime']
      events = service.get_events(calendarId=order.google_calendar_id,min_date=min_date,max_date=max_date)
      accepted_orders = []
      for item in events['items']:
            try:
                  if ((item['extendedProperties']['private']['status']=="accepted" 
                  and item['extendedProperties']['private']['event_type']=="order")
                  or item['extendedProperties']['private']['event_type']=="busy"
                  or item['extendedProperties']['private']['event_type']=="non-working"):
                        accepted_orders.append(item)
            except:
                  pass

      if len(accepted_orders)>0:
            return Response({"message":"You can not accept this order with this date."},status=400)
      else:
            order.status="accepted"
            order.save()
            event = service.get_event(calendar_id=order.google_calendar_id,event_id=order.google_event_id)
            event["extendedProperties"]['private']['status'] ="accepted"
            service.update_event(calendar_id=order.google_calendar_id, 
                                    event_id=order.google_event_id, 
                                    body=event)
            send_notification("AO",owner=order.user_id,
                              fullname_user=order.master_id,
                              service=order.service_id)
            if has_automated_cancelation is not None and has_automated_cancelation==True:
                  for pending_order in Order.objects.filter(status="pending"):
                        transactions = Transaction.objects.filter(pending_order_id = pk)
                        for transaction in transactions:
                              stripe.Refund.create(payment_intent=transaction.payment_id)
                              transaction.status='refunded'
                              transaction.save()
                        if pending_order.user.user.email is not None and pending_order.user.user.email !="":
                              lang = "EN"
                              if pending_order.user.settings.all().count()>0:
                                    lang = pending_order.user.settings.all().first().language.code
                              send_email(to_email=pending_order.user.user.email,
                                    code="CNCO",
                                    service_name=+pending_order.service.name_fr if lang == "FR" else pending_order.service.name_en,
                                    lang=lang)

                        try:
                              send_notification("COM",owner=pending_order.user_id,
                                                fullname_user=pending_order.master_id,
                                                service=pending_order.service_id)
                        except:
                              pass
                        pending_order.status="cancelled"
                        try:
                              pending_order.cancel_reason = "Many order for same time."
                        except:
                              pass
                        pending_order.save()
                        event = service.get_event(calendar_id=pending_order.google_calendar_id,event_id=pending_order.google_event_id)
                        event["extendedProperties"]['private']['status'] ="cancelled"
                        service.update_event(calendar_id=pending_order.google_calendar_id, 
                                                event_id=pending_order.google_event_id, 
                                                body=event)
                        ScheduledPushNotification.objects.filter(pending_order_id = pk).delete()
            return Response(OrderSerializer(order).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_login(request):
      account = stripe.Account.create(
            type='express',
      )
      is_mobile = request.GET.get("is_mobile",None)
      if is_mobile:
            account_links = stripe.AccountLink.create(
                  account=account['id'],
                  refresh_url="{0}://{1}".format('https', request.get_host()) + "/schedule/check-stripe/"+str(request.user.id)+"/"+str(account['id'])+"/?is_mobile=true&redirect_url="+str(request.GET.get("redirect_url", None)),
                  return_url="{0}://{1}".format('https', request.get_host()) + "/schedule/check-stripe/"+str(request.user.id)+"/"+str(account['id'])+"/?is_mobile=true&redirect_url="+str(request.GET.get("redirect_url", None)),
                  type='account_onboarding',
                  )
      else:
            account_links = stripe.AccountLink.create(
                  account=account['id'],
                  refresh_url="{0}://{1}".format('https', request.get_host()) + "/schedule/check-stripe/"+str(request.user.id)+"/"+str(account['id'])+"/",
                  return_url="{0}://{1}".format('https', request.get_host()) + "/schedule/check-stripe/"+str(request.user.id)+"/"+str(account['id'])+"/",
                  type='account_onboarding',
                  )
      return Response({"redirect_url":account_links['url']})

class CustomRedirect(HttpResponsePermanentRedirect):
      allowed_schemes = ['beautycils','http','https']

@api_view(['GET'])
def check_stripe(request,pk,id): 
      is_mobile=request.GET.get("is_mobile",None)
      account = stripe.Account.retrieve(id)
      if account['object']=="account":
            user_details = UserDetail.objects.get(user_id=pk)
            user_details.stripe_client_id = account['id']
            user_details.save()
            if is_mobile:
                  return CustomRedirect(request.GET.get("redirect_url"))
            else:
                  return redirect("https://beautycils.app/payment-cards/add-card?stripe=true")
      else:
            if is_mobile:
                  return CustomRedirect(request.GET.get("redirect_url"))
            else:
                  return redirect("https://beautycils.app/payment-cards/add-card")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_card(request):
      user = UserDetail.objects.get(user_id = request.user.id)
      if user.stripe_customer_id is None:
            customer = stripe.Customer.create()
            user.stripe_customer_id = customer['id']
            user.save()
      payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                  "number":request.data['number'],
                  "exp_year":request.data['exp_year'],
                  "exp_month":request.data['exp_month'],
                  "cvc":request.data['cvc'],
            },
            metadata={
                  "name":request.data['name'],
                  "email":request.data['email'],
                  "phone_number":request.data['phone_number'],
            })
      setup_intent = stripe.SetupIntent.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            confirm=True,
            payment_method = payment_method['id'],
            return_url = "https://api.beautycils.app/schedule/payment-intent-to-costumer/?pm="+\
                  payment_method['id']+"&cid="+user.stripe_customer_id+"&rurl="+request.GET.get("rurl")
            )
      if setup_intent['status'] == "succeeded":
            stripe.PaymentMethod.attach(payment_method['id'],customer=user.stripe_customer_id)
      return Response(setup_intent)

@api_view(['GET'])
def payment_intent_to_costumer(request):
      try:
            stripe.PaymentMethod.attach(
                  request.GET.get("pm"),
                  customer=request.GET.get("cid"),
                  )
            return CustomRedirect(request.GET.get("rurl")+"?status=succeed")
      except:
            return CustomRedirect(request.GET.get("rurl")+"?status=failed")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cards(request):
      try:
            user = UserDetail.objects.get(user_id = request.user.id)
            cards = stripe.PaymentMethod.list(customer=user.stripe_customer_id,limit=100,type="card")
            return Response(cards)
      except:
            return Response({"message":"Something went wrong"},status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_card(request):

      stripe.PaymentMethod.detach(
             request.GET.get("card_id"),
            )
      return Response({"message":"OK"},status=200)

def pay_stripe(request, price, transaction):
      application_fee = General.objects.all().first().application_fee
      user = UserDetail.objects.get(user_id = request.user.id)
      if user.stripe_customer_id is None:
            customer = stripe.Customer.create()        
            user.stripe_customer_id = customer['id']
            user.save()

      payment_intent = stripe.PaymentIntent.create(
            amount=int(price*100),
            currency="eur",
            # application_fee_amount = int(price*100) - round(float(int(price*100))*(100-application_fee)/100),
            payment_method=request.data['existing_card'],
            payment_method_types=["card"],
            customer=user.stripe_customer_id,
            transfer_data={
                  "destination":user.stripe_client_id
            },
            payment_method_options={
                  "card":{
                        "request_three_d_secure":"automatic"
                        }
                  },
            # on_behalf_of=user.stripe_client_id
            )
      payment_intent_confirm = stripe.PaymentIntent.confirm(
            payment_intent['id'],
            return_url="{0}://{1}".format('https', str(request.get_host())) + "/schedule/check-payment/"+str(payment_intent.id)+"/"+str(transaction.id)+"/?rurl="+str(request.GET.get("rurl",None))
      )
      return payment_intent_confirm

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_calendar_by_date(request):
      user = UserDetail.objects.get(id=request.data['master_id'])
      min_date = str(datetime.strptime(request.data['date']+"T00:00:00",'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = str(datetime.strptime(request.data['date']+"T23:59:59",'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      events = service.get_events(calendarId=user.google_calendar_id,min_date=min_date,max_date=max_date)
      other_events = []

      for item in events['items']:
            try:
                  if (item['extendedProperties']['private']['event_type']=="busy"
                  or item['extendedProperties']['private']['event_type']=="working"
                  or  item['extendedProperties']['private']['event_type']=="non-working"):
                        other_events.append(item)
            except:
                  pass
      order_events = []
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['event_type']=="order":
                        order_events.append(item['id'])
            except:
                  pass
      orders = Order.objects.filter(master_id=request.data['master_id'],google_event_id__in=order_events)
      return Response({
            "other_events":other_events,
            "orders":OrderSerializer(orders,many=True).data
            })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_monthly_orders(request):
      master = UserDetail.objects.get(id=request.data["master_id"])
      start_date = request.data['start_date']
      end_date = request.data['end_date']
      min_date = str(datetime.strptime(start_date+"T00:00:00",'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      max_date = str(datetime.strptime(end_date+"T23:59:59",'%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      events = service.get_events(calendarId=master.google_calendar_id,min_date=min_date,max_date=max_date)
      order_event_ids = []
      order_events = []
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['event_type']=="order":
                        order_event_ids.append(item['id'])
                        order_events.append(item)
            except:
                  pass
      orders = Order.objects.filter(master_id=request.data['master_id'],google_event_id__in=order_event_ids)
      result = {}
      for order in orders:
            if order.status == "accepted" or order.status == "pending":
                  for oe in order_events:
                        if order.google_event_id == oe['id']:
                              date = oe['start']['dateTime'][0:10]
                              if date not in result.keys():
                                    result[date]={"accepted":0,"pending":0}
                              result[date][order.status]+=1
      res_array = []
      for i in result.keys():
            res_array.append({"date":i,"accepted":result[i]['accepted'],"pending":result[i]['pending']})
      return Response(res_array)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_master_clients(request,pk):
      paginator = PageNumberPagination()
      paginator.page_size = request.GET.get("limit",10)
      qs = UserDetail.objects.filter(user_orders__master_id = pk).distinct()
      users = paginator.paginate_queryset(qs, request)
      result = []
      for i in users:
            obj = ClientDetailSerializer(i).data
            obj['join_date'] = str(i.user_orders.all().order_by("id").first().start_date)
            result.append(obj)
      return paginator.get_paginated_response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_client_masters(request,pk):
      paginator = PageNumberPagination()
      paginator.page_size = request.GET.get("limit",10)
      qs = UserDetail.objects.filter(master_orders__user_id = pk).distinct()
      search = request.GET.get('search')
      if search is not None:
            qs = qs.filter(Q(user__first_name__icontains = search) | Q(user__last_name__icontains = search))
      users = paginator.paginate_queryset(qs, request)
      return paginator.get_paginated_response(MasterSerializer(users,many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_daily_schedule_by_service(request):
      service_id = request.data['service']
      calendar_id = request.data['calendar_id']
      start_date = str(datetime.strptime(request.data['date'] +" 00:00:00",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      end_date = str(datetime.strptime(request.data['date'] +" 23:59:59",'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'))+"-00:00"
      interval = request.data['interval']
      events = service.get_events(calendarId=calendar_id,min_date=start_date,max_date=end_date)
      is_non_working_day = False
      try:
            for item in events['items']:
                  if item['extendedProperties']['private']['event_type']=="non-working":
                        is_non_working_day=True
                        break
      except:
            pass
      if is_non_working_day:
            return Response({"message":"Day is non working day","error":"nwd"},status=400)
      working_days = []
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['event_type']=="working" \
                        and (item['extendedProperties']['shared'][str(service_id)]==True\
                        or item['extendedProperties']['shared'][str(service_id)]=="true"\
                        or item['extendedProperties']['shared'][str(service_id)]=="True"):
                        working_days.append(item)
            except:
                  pass
      if len(working_days) == 0:
            return Response({"message":"No available time for this service in this day.",
                                    "error":"nat"},status=400)
      timings = []
      for event in working_days:
            obj = {
                  "start":event['start']['dateTime'],
                  "end":event['end']['dateTime']
            }
            if obj in timings:
                  pass
            else:
                  timings.append(obj)
      timings = sorted(timings, key = lambda i: i['start'])

      # busy_dates = [{"start_date":item.start_date,"end_date":item.end_date,} for item in Order.objects.filter(
      #                                           master_id = master.id, 
      #                                           start_date__date = request.data['date']).filter(
      #                                           Q(status="accepted") | Q(status="done") | Q(status="passed"))]
      
      for i in range(1,len(timings)):
            intervals = []
            for index,time in enumerate(timings):
                  if index+1 == len(timings):
                        intervals.append(time)
                  elif timings[index+1]['start']>=time['start'] and timings[index+1]['start']<=time['end']:
                        intervals.append({
                              "start":time['start'],
                              "end":timings[index+1]['end']
                        })
                        if index == len(timings)-2:
                              break
                  else:
                        intervals.append(time)
            timings = intervals
      ints = []
      aa = []
      for time in timings:
            start = datetime.strptime(time['start'],'%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M:%S")
            end = datetime.strptime(time['end'],'%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M:%S")
            FMT = '%H:%M:%S'
            tdelta = ((datetime.strptime(end, FMT) - datetime.strptime(start, FMT))).total_seconds()
            st = datetime.strptime(time['start'],'%Y-%m-%dT%H:%M:%SZ')
            
            for _ in range(math.floor((tdelta/60)/interval)):
                  date = str(request.data['date'])+" "+str(st.strftime("%H:%M:%S"))
                  start_time = datetime.strptime(str(date),'%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%dT%H:%M:%SZ")
                  end_time = datetime.strptime(str(datetime.strptime(date,"%Y-%m-%d %H:%M:%S")+timedelta(minutes = interval)),'%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%dT%H:%M:%SZ")
                  time_events = service.get_events(calendarId=request.data['calendar_id'],
                                          min_date=start_time,
                                          max_date=end_time)
                  evs = []
                  ed = None
                  sd=None
                  for item in time_events['items']:
                        # try:
                        if "extendedProperties" in item:
                              if "private" in item['extendedProperties']:
                                    i = item['extendedProperties']['private']
                                    if (i['event_type']=="busy"
                                    or  i['event_type']=="non-working"
                                    or (i['event_type']=="order"
                                    and ("status" in i) and i['status'] == "accepted" )):
                                          evs.append(item)
                                          sd = datetime.strptime(str(datetime.strptime(item['start']['dateTime'],'%Y-%m-%dT%H:%M:%SZ')),"%Y-%m-%d %H:%M:%S")
                                          ed = datetime.strptime(str(datetime.strptime(item['end']['dateTime'],'%Y-%m-%dT%H:%M:%SZ')),"%Y-%m-%d %H:%M:%S")
                                    if i['event_type']=="order":
                                          aa.append(item)
                        # except:
                        #       pass
                  if len(evs)==0:
                        ints.append({
                              "start_time":request.data['date']+"T"+str(st.strftime("%H:%M"))+":00.000Z",
                              "end_time":request.data['date']+"T"+str((st+timedelta(minutes = interval)).strftime("%H:%M"))+":00.000Z",
                              "is_available":True
                              })
                        st = st + timedelta(minutes = interval)
                  else:
                        ints.append({
                              "start_time":str(sd).replace(" ","T")+".000Z",
                              "end_time":str(ed).replace(" ","T")+".000Z",
                              "is_available":False
                              })
                        st = ed
      return Response(ints)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_for_order(request, pk):
      order = Order.objects.get(id=pk)
      price = order.price-order.prepayed_price
      transaction = Transaction(amount=price,
                                    payment_id="some key",
                                    status="pending",
                                    order=order,
                                    client_id=order.user.id,
                                    master_id = order.master.id)
      transaction.save()
      user = UserDetail.objects.get(user__id = request.user.id)
      if user.stripe_customer_id is None:
            customer = stripe.Customer.create()        
            user.stripe_customer_id = customer['id']
            user.save()

      payment_intent = stripe.PaymentIntent.create(
            amount=int(price*100),
            currency="eur",
            payment_method=request.data['existing_card'],
            payment_method_types=["card"],
            customer=user.stripe_customer_id,
            payment_method_options={
                  "card":{
                        "request_three_d_secure":"automatic"
                        }
                  },
            on_behalf_of = user.stripe_client_id
            )
      payment_intent_confirm = stripe.PaymentIntent.confirm(
            payment_intent['id'],
            return_url="{0}://{1}".format('https', str(request.get_host())) + "/schedule/check-full-payment/"+str(payment_intent.id)+"/"+str(transaction.id)+"/?rurl="+request.GET.get("rurl",None)
      )
      transaction.payment_id = payment_intent_confirm['id']
      transaction.save()
      redirect_url = str(payment_intent_confirm['id'])+"/"+str(transaction.id)+"/"
            
      if payment_intent_confirm['status'] == "succeeded":
            return Response({"redirect_url":redirect_url,"do_redirection":True},status=200)
      else:
            return Response({"iframe_url":payment_intent_confirm['next_action']['redirect_to_url']['url']},status=200)

@api_view(['GET'])
def check_full_payment(request, id, pk):
      transaction = Transaction.objects.get(id=pk)
      order = Order.objects.get(id=transaction.order_id)
      if stripe.PaymentIntent.retrieve(id)['status'] == "succeeded":
            order.payment_status = "succeed"
            order.payed_by_cache = False
            order.save()
            transaction.status="succeed"
            transaction.save()
            try:
                  send_notification("FOP",owner=order.master_id,
                                          fullname_user=order.user_id,
                                          service=order.service_id)
            except:
                  pass
            if request.GET.get("rurl") is not None:
                  return CustomRedirect(request.GET.get("rurl")+"?status=succeed")
            else:
                  return Response({"ok":True},status=200)
      else:
            transaction.delete()
            if request.GET.get("rurl") is not None:
                  return CustomRedirect(request.GET.get("rurl")+"?status=failed")
            else:
                  return Response({"ok":False},status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_working_events(request):
      master_services = MasterService.objects.filter(user_id=request.GET.get('master_id'))
      try:
            events = service.get_all_events(master_services.first().user.google_calendar_id)
      except:
            return Response({"message":"Master has no services"},status=400)
      res = []
      for item in events['items']:
            try:
                  if item['extendedProperties']['private']['event_type']=="working":
                        recurrece_text = str(item['recurrence'])
                        start_index = recurrece_text.find("UNTIL=",0,80)+6
                        datetimee = recurrece_text[start_index:start_index+16]
                        res.append({
                              "services":item['extendedProperties']['shared'].keys(),
                              "event_id":item['id'],
                              "start_date":item['start']['dateTime'],
                              "end_date":datetime.strptime(datetimee, '%Y%m%dT%H%M%SZ').strftime("%Y-%m-%dT%H:%M:%SZ"),
                              "recurrence":"daily" if str(item['recurrence'])[2:18] == "RRULE:FREQ=DAILY" else "weekly",
                              "week_day":None if str(item['recurrence'])[2:18] == "RRULE:FREQ=DAILY" else recurrece_text[recurrece_text.find("BYDAY=",0,80)+6:][:-2],                        
                              })
            except:
                  pass
      result = []
      for master_service in master_services:
            result.append({
                  "service":MasterService2Serializer(master_service).data,
                  "schedules":[i for i in res if str(master_service.service.id) in i['services']]
            })
      return Response(result)

@api_view(['GET'])
def delete(request):
      i = 0
      for user in UserDetail.objects.all():
            if user.google_calendar_id is not None and user.google_calendar_id != "":
                  for event in service.get_all_events(calendarId=user.google_calendar_id)['items']:
                        i+=1
                        try:
                              service.delete_event(user.google_calendar_id, event['id'])
                        except:
                              pass

      return Response(True)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_service_availability(request,pk):
      count = Order.objects.filter(service_id=pk, user__user_id = request.user.id).exclude(
                              Q(status="cancelled") | Q(status="done") | Q(status="passed")).count()
      return Response({"available":count==0}, status = 200)

def send_done_push(order_id):
      order = Order.objects.get(id=order_id)
      item = NotificationType.objects.get(code="SDP")
      lang = "EN"
      langs = order.user.settings.all()
      for lan in langs:
            lang = lan.language.code
            break
      if lang == "FR":
            text=item.text_fr
      else:
            text=item.text_en
      text = text.replace("<<USERNAME<<",str(order.master.user.first_name)+str(order.master.user.last_name))
      text = text.replace("<<SERVICE<<",order.service.name_en if lang=="EN" else order.service.name_fr)
      for i in order.user.push_tokens.all():
            send_push(to=i.token,title="",body=text)
