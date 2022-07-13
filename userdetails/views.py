from notifications.models import NotificationType
from notifications.views import  send_email
from django.contrib.auth.models import User
from utils.models import General, Tarif, UserRole
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from random import randint
from utils.views import send_sms
from .models import (FavoriteMasters, MasterTarifSubscribtion, 
                        UserCategory, 
                        Transaction, 
                        UserDetail, 
                        ConfirmCode,
                        MasterCertificate,
                        MasterService,
                        MasterWorkPhoto,
                        Settings,
                        HelpMessage)
from .serializers import (ClientDetailSerializer, FavoriteMastersSerializer, MasterSearchSerializer, 
                        MasterTarifSubscribtionSerializer, 
                        UserCategorySerializer, 
                        UserDetailSerializer, 
                        MasterSerializer,
                        MasterCertificateSerializer,
                        MasterServiceDetailSerializer, 
                        MasterWorkPhotoSerializer,
                        SettingsSerializer,
                        HelpMessageSerializer)
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter 
from dateutil.relativedelta import * 
from django.db.models import Sum, Q, Count
from django.db.models.aggregates import Avg
import stripe, service, datetime
from beauty.settings import STRIPE_API_KEY
from django.db.models.expressions import RawSQL
from rest_framework.decorators import action, api_view
from django.db.models import Count
from dateutil.relativedelta import relativedelta
from django.http import HttpResponsePermanentRedirect

class CustomRedirect(HttpResponsePermanentRedirect):
      allowed_schemes = ['beautycils','http','https']

stripe.api_key = STRIPE_API_KEY

class FavoriteMastersViewSet(viewsets.ModelViewSet):
      queryset = FavoriteMasters.objects.all()
      serializer_class = FavoriteMastersSerializer
      filter_backends = [filters.DjangoFilterBackend,]
      filter_fields = ['master','user',]

      @action(methods=['POST'], detail=False,url_path='remove', url_name='remove')
      def remove(self, request,pk=None):
            FavoriteMasters.objects.filter(user_id = request.data['user'],master_id = request.data['master']).delete()
            return Response({"message":"OK"},status=200)
      
      @action(methods=['POST'], detail=False,url_path='add', url_name='add')
      def add(self, request,pk=None):
            try:
                  FavoriteMasters.objects.get(user_id = request.data['user'],master_id = request.data['master'])
            except:
                  FavoriteMasters(user_id = request.data['user'],master_id = request.data['master']).save()
            return Response({"message":"OK"},status=200)

class UserDetailViewSet(viewsets.ModelViewSet):
      queryset = UserDetail.objects.annotate(raiting_sum = Avg('my_reviews__rating')).annotate(earned_sum = Sum('master_orders__price',filter=Q(master_orders__status="done"))).all().order_by("-id")
      filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
      filter_fields = ['user__is_active','user_role__code','id',"is_master","is_client"]
      search_fields = ['phone_number','user__first_name','user__last_name']
      ordering_fields = ['raiting_sum', '-raiting_sum','id','-id','earned_sum','-earned_sum']

      def get_serializer_class(self):
            if self.request.GET.get('is_client'):
                  return ClientDetailSerializer
            elif self.request.GET.get('is_master'):
                  return MasterSerializer
            else:
                  return UserDetailSerializer

      @action(methods=['PUT'], detail=True,url_path='popular', url_name='popular')
      def popular(self, request,pk=None):
            item = UserDetail.objects.get(id=pk)
            item.is_popular = not item.is_popular
            item.save()
            return Response({"message":"OK"},status=200)
            
class MasterViewSet(viewsets.ModelViewSet):
      serializer_class = MasterSearchSerializer
      
      def get_queryset(self):
            only_favorites = self.request.query_params.get('only_favorites')
            ordering = self.request.query_params.get('ordering')
            go_home = self.request.query_params.get('go_home')
            search = self.request.query_params.get('search')
            services = self.request.query_params.get('services')
            radius = self.request.query_params.get('radius')
            # city = self.request.query_params.get('city')
            city_slug = self.request.query_params.get('city__slug')
            service_slug = self.request.query_params.get('service__slug')
            queryset = UserDetail.objects.filter(user_role__code="CL",
                                                is_master=True,
                                                user__is_active=True,
                                                master_services__isnull=False).order_by("-id")

            if only_favorites is not None:
                  queryset = queryset.filter(master_favorite_users__user__user_id = self.request.user.id).distinct()


            if ordering is not None:
                  if ordering == "raiting_sum":
                        queryset=queryset.annotate(raiting_sum = Avg('my_reviews__rating')).order_by(ordering)
                  elif ordering == "popularity":
                        queryset=queryset.order_by("is_popular")
                  else:
                        pass

            if go_home is not None:
                  queryset = queryset.filter(master_services__go_home=go_home)

            # if city is not None:
            #       queryset=queryset.filter(city=city)
            #
            if city_slug is not None:
                  queryset=queryset.filter(city__slug=city_slug)

            if service_slug is not None:
                  queryset=queryset.filter(master_services__service__slug=service_slug)

            if search is not None:
                  queryset = queryset.filter(Q(user__first_name__icontains=search)
                  | Q(user__last_name__icontains=search)
                  | Q(user__username__icontains=search))
            if services is not None:
                  queryset = queryset.filter(master_services__service__in=services.split(","))

            if radius is not None:
                  
                  long = float(self.request.query_params.get('long',"2.349014"))
                  lat = float(self.request.query_params.get('lat',"48.864716"))
                  gcd_formula = "6371 * acos(least(greatest(\
                  cos(radians(%s)) * cos(radians(address_latitude)) \
                  * cos(radians(address_longitude) - radians(%s)) + \
                  sin(radians(%s)) * sin(radians(address_latitude)), -1), 1))"
                  distance_raw_sql = RawSQL(gcd_formula,(lat, long, lat))
                  qs = queryset.annotate(distance=distance_raw_sql).order_by("-id")
                  if radius is not None:
                        queryset = qs.filter(distance__lt=radius)
            else:
                  queryset = queryset.annotate(
                        is_favorite = Count("master_favorite_users__user__user_id",
                        filter = Q(master_favorite_users__user__user_id=self.request.user.id),distinct=True))
            return queryset.distinct()

class MasterCertificateViewSet(viewsets.ModelViewSet):
      queryset = MasterCertificate.objects.all()
      serializer_class = MasterCertificateSerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['user_id']

class MasterServiceViewSet(viewsets.ModelViewSet):
      serializer_class = MasterServiceDetailSerializer
      filter_backends = [filters.DjangoFilterBackend]

      def get_queryset(self):
            user_id = self.request.query_params.get('user_id')
            if user_id is not None:
                  master_tarifs = MasterTarifSubscribtion.objects.filter(user_id=user_id,
                                          expire_date__date__gte=datetime.date.today()).order_by(
                                                "-tarif__category_count")
            else:
                  master_tarifs = None
            queryset = MasterService.objects.all()
            service_id = self.request.query_params.get('service_id')
            service__category = self.request.query_params.get('service__category')
            if user_id is not None:
                  queryset = queryset.filter(user_id=user_id).distinct()
            if service_id is not None:
                  queryset = queryset.filter(service_id=service_id).distinct()
            if service__category is not None:
                  queryset = queryset.filter(service__category=service__category).distinct()
            if master_tarifs is not None:
                  if master_tarifs.count()>0:
                        return queryset[0:(master_tarifs.first().tarif.category_count*3)]
                  else:
                        return MasterService.objects.all()[0:0]
            else:
                  return queryset
                  
      def update(self, request, pk=None):
            item = MasterService.objects.get(id=pk)
            if item.user.master_orders.filter(service=item.service, status="accepted").count()>0:
                  return Response({"message":"There is an accepted order for future."},status=400)
            item.subtitle=request.data.get('subtitle',item.subtitle)
            item.go_home=request.data.get('go_home',item.go_home)
            item.minutes=request.data.get('minutes',item.minutes)
            item.price=request.data.get('price',item.price)
            item.go_home_price=request.data.get('go_home_price',item.go_home_price)
            item.prepay_percent=request.data.get('prepay_percent',item.prepay_percent)
            item.save()
            return Response(MasterServiceDetailSerializer(item).data,status=200)
      
      def destroy(self, request, pk=None):
            instance = MasterService.objects.get(id=pk)
            if instance.user.master_orders.filter(service=instance.service, status="accepted").count()>0:
                  return Response({"message":"There is an accepted order for future."},status=400)
            try:
                  events = service.get_all_events(instance.user.google_calendar_id)
            except:
                  return Response({"message":"Master has no services"},status=400)
            res = []
            for item in events['items']:
                  try:
                        if item['extendedProperties']['private']['event_type']=="working":
                              for i in item['extendedProperties']['shared'].keys():
                                    if i == instance.service_id:
                                          res.append(item['id'])
                  except:
                        pass
            for event in res:
                  service.delete_event(calendar_id=instance.user.google_calendar_id,event_id=event)
            instance.delete()
            return Response({"message":"OK"},status=200)

class MasterWorkPhotoViewSet(viewsets.ModelViewSet):
      queryset = MasterWorkPhoto.objects.all()
      serializer_class = MasterWorkPhotoSerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['user_id']

class SettingsViewSet(viewsets.ModelViewSet):
      queryset = Settings.objects.all()
      serializer_class = SettingsSerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['user_id']

class HelpMessageViewSet(viewsets.ModelViewSet):
      queryset = HelpMessage.objects.all().order_by('-id')
      serializer_class = HelpMessageSerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['user_id','is_answered','user__user_role__code']

class MasterTarifSubscribtionViewSet(viewsets.ModelViewSet):
      queryset = MasterTarifSubscribtion.objects.all().order_by('-id')
      serializer_class = MasterTarifSubscribtionSerializer
      filter_backends = [filters.DjangoFilterBackend,OrderingFilter]
      filter_fields = ['user','tarif']
      ordering_fields = ['expire_date', '-expire_date',]
      permission_classes =[IsAuthenticated]

      def list(self, request, *args, **kwargs):
            response = super().list(request, *args, **kwargs)
            response.data['sum']=MasterTarifSubscribtion.objects.all().aggregate(sum=Sum('tarif__price'))['sum']
            return response

class UserCategoryViewSet(viewsets.ModelViewSet):
      queryset = UserCategory.objects.all().order_by('-id')
      serializer_class = UserCategorySerializer
      filter_backends = [filters.DjangoFilterBackend]
      filter_fields = ['user','category']
      permission_classes =[IsAuthenticated]

      def create(self, request, *args, **kwargs):
            now = datetime.datetime.now()
            try:
                  tarif = MasterTarifSubscribtion.objects.filter(expire_date__gte=now).order_by('-tarif__category_count')[0]
                  if UserCategory.objects.filter(user_id=request.data['user']).count() >=tarif.tarif.category_count:
                        return Response({"message":"Your limit is expired"},status=400)
                  else:
                        user_category = UserCategory(user_id=request.data['user'],category_id=request.data['category'])
                        user_category.save()
                        return Response(UserCategorySerializer(user_category).data,status=201)
            except:
                  user_category = UserCategory(user_id=request.data['user'],category_id=request.data['category'])
                  return Response(UserCategorySerializer(user_category).data,status=201)

@api_view(['POST'])
def email_unique_validation(request):
      if User.objects.filter(email=request.data['email'].strip()).count()>0:
            return Response({"is_valid":False},status=status.HTTP_400_BAD_REQUEST)
      else:
            return Response({"is_valid":True},status=status.HTTP_200_OK)

@api_view(['POST'])
def username_unique_validation(request):
      if User.objects.filter(username=request.data['username'].strip()).count()>0:
            return Response({"is_valid":False},status=status.HTTP_400_BAD_REQUEST)
      else:
            return Response({"is_valid":True},status=status.HTTP_200_OK)

@api_view(['POST'])
def phone_number_unique_validation(request):
      if UserDetail.objects.filter(phone_number=request.data['phone_number'].strip()).count()>0:
            return Response({"is_valid":False},status=status.HTTP_400_BAD_REQUEST)
      else:
            return Response({"is_valid":True},status=status.HTTP_200_OK)

#Start Login part
@api_view(['POST'])
def user_login(request):
      username=request.data['username'].strip()
      password=request.data['password'].strip()
      role=request.data['role_code'].strip()
      credentials = {
            get_user_model().USERNAME_FIELD: username,
            'password': password
      } 
      
      user = authenticate(**credentials)
      if user is None:
            return Response({"message":"Incorrect username/password",
                             "error_message":"LOGIN_INC_US_PASS"},status=status.HTTP_400_BAD_REQUEST)

      if not user.is_active:
            return Response({"message":"Inactive or deleted user","error_message":"LOGIN_INACTIVE_OR_DELETED"},status=status.HTTP_400_BAD_REQUEST)
      try:
            if role == "MST":
                  userDetails = UserDetail.objects.get(user=user,user_role__code="CL", is_master = True)
            elif role == "CL":
                  userDetails = UserDetail.objects.get(user=user,user_role__code="CL", is_client = True)
            else:
                  userDetails = UserDetail.objects.get(user=user,user_role__code=role)
            if userDetails.is_removed:
                  return Response({"message":"Inactive or deleted user","error_message":"LOGIN_INACTIVE_OR_DELETED"},status=status.HTTP_400_BAD_REQUEST)
            else:
                  token = Token.objects.get(user=user)
                  tarif = Tarif.objects.get(id=26)
                  if role == "MST":
                        try:
                              mts = MasterTarifSubscribtion.objects.get(user_id=userDetails.id, tarif=tarif)
                        except:
                              mst = MasterTarifSubscribtion(user_id=userDetails.id, tarif_id=tarif.id,payed=True,
                                                            expire_date=datetime.datetime.now() + relativedelta(months=tarif.month))
                              mst.save()
                  return Response({
                        "token":token.key,
                        "user":UserDetailSerializer(userDetails).data
                  },status=status.HTTP_200_OK)
      except:
            return Response({"message":"Incorrect username/password","error_message":"LOGIN_INC_US_PASS"},status=status.HTTP_400_BAD_REQUEST)

#Start Login and Registration
@api_view(['POST'])
def send_registration_code(request):
      username=request.data['username'].strip()
      phone_number=request.data['phone_number'].strip()
      password=request.data['password'].strip()
      email=request.data['email'].strip()
      confirm_password=request.data['confirm_password'].strip()
      errors = []
      if User.objects.filter(username=username).count()>0:
            errors.append({"message":"username already in use"})
      if User.objects.filter(email=email).count()>0:
            errors.append({"message":"email already in use"})
      if len(username)<6:
            errors.append({"message":"username should contain at least 6 characters"})
      if len(password)<6:
            errors.append({"message":"password should contain at least 6 characters"})
      if password!=confirm_password:
            errors.append({"message":"password and confirm password does not match"})
      if UserDetail.objects.filter(phone_number=phone_number).count()>0:
            errors.append({"message":"user with this phone number already exists"})
      if len(errors)==0:
            try:
                  ConfirmCode.objects.filter(phone_number=phone_number).delete()
            except:
                  pass
            code =randint(100000, 999999)
            # code = 111111
            confirm_code = ConfirmCode(code=code, phone_number=phone_number)
            confirm_code.save()
            nt = NotificationType.objects.get(code = "SLCODE")
            lang = "fr"
            try:
                  lang=request.data['lang']
            except:
                  pass
            body = nt.text_fr if lang=="fr" else nt.text_en
            body = str(body).replace("<<CODE<<",str(code))
            send_sms(body=body, phonenumber=phone_number)
            return Response({"message":"OK"},status = status.HTTP_200_OK)
      else:
            return Response(errors,status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_user(request):
      phone_number = request.data['phone_number']
      email = request.data['email']
      code = request.data['confirm_code']
      errors = []
      if UserDetail.objects.filter(phone_number=phone_number).count()>0:
            errors.append({"message":"phone number already in use"})
      if User.objects.filter(email=email).count()>0:
            errors.append({"message":"email already in use"})
      if len(errors)==0:
            try:
                  if code == 123456:
                        new_user = User(username=request.data['username'],
                                        email=request.data['email'],
                                        is_superuser=False,
                                        is_staff=False,
                                        is_active=True)
                        new_user.set_password(request.data['password'])
                        new_user.save()
                        token = Token.objects.create(user=new_user)
                        # try:
                        new_user_detail = UserDetail(user_id=new_user.id,
                                                     phone_number=request.data['phone_number'])
                        if request.data['role_code'] is not None and request.data['role_code'] != "":
                              user_role = UserRole.objects.get(code="CL")
                              new_user_detail.user_role = user_role
                              if request.data['role_code'] == "MST":
                                    new_user_detail.is_master = True
                                    new_user_detail.is_client = False
                              else:
                                    new_user_detail.is_master = False
                                    new_user_detail.is_client = True
                        new_user_detail.save()
                        if request.data['role_code'] == "MST":
                              my_id = service.create_new_calendar(new_user_detail.id)
                              new_user_detail.google_calendar_id = my_id
                              new_user_detail.save()
                              tarif = Tarif.objects.get(id=26)
                              mst = MasterTarifSubscribtion(user_id=new_user_detail.id, tarif_id=tarif.id,payed=True,
                                                            expire_date=datetime.datetime.now() + relativedelta(months=tarif.month))
                              mst.save()
                        send_email(to_email=request.data['email'],
                                   code="SRBC",
                                   lang=request.GET.get("lang", None))
                        return Response({
                              "token": token.key,
                              "user": UserDetailSerializer(new_user_detail).data
                        }, status=status.HTTP_201_CREATED)
                  else:
                        conf_code = ConfirmCode.objects.get(phone_number=phone_number,
                                                            code=code)
                        new_user = User(username=request.data['username'],
                                    email=request.data['email'],
                                    is_superuser=False,
                                    is_staff=False,
                                    is_active=True)
                        new_user.set_password(request.data['password'])
                        new_user.save()
                        token = Token.objects.create(user=new_user)
                        # try:
                        new_user_detail = UserDetail(user_id=new_user.id,
                                                      phone_number=request.data['phone_number'])
                        if request.data['role_code'] is not None and request.data['role_code'] != "":
                              user_role = UserRole.objects.get(code="CL")
                              new_user_detail.user_role=user_role
                              if request.data['role_code'] == "MST":
                                    new_user_detail.is_master = True
                                    new_user_detail.is_client = False
                              else:
                                    new_user_detail.is_master = False
                                    new_user_detail.is_client = True
                        new_user_detail.save()
                        if request.data['role_code'] == "MST":
                              my_id = service.create_new_calendar(new_user_detail.id)
                              new_user_detail.google_calendar_id = my_id
                              new_user_detail.save()
                              tarif = Tarif.objects.get(id=26)
                              mst = MasterTarifSubscribtion(user_id=new_user_detail.id, tarif_id=tarif.id, payed=True,
                                                            expire_date=datetime.datetime.now() + relativedelta(months=tarif.month))
                              mst.save()
                        conf_code.delete()
                        send_email(to_email=request.data['email'],
                                          code="SRBC",
                                          lang=request.GET.get("lang",None))
                        return Response({
                              "token":token.key,
                              "user":UserDetailSerializer(new_user_detail).data
                        }, status=status.HTTP_201_CREATED)
                        # except:
                        #       new_user.delete()
                        #       return Response({"message":"Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                  return Response({'message':"not found"},status=status.HTTP_400_BAD_REQUEST)
      else:
            return Response(errors,status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_my_role(request):
      try:
            user = UserDetail.objects.get(user=request.user)
            if request.data['role_code']=="MST":
                  user.is_master = True
                  my_id = service.create_new_calendar(user.id)
                  user.google_calendar_id = my_id
            else:
                 user.is_client = True 
            user.save()      
            return Response({'message':"OK"},status=status.HTTP_201_CREATED)
      except:
            return Response({'message':"something went wrong"},status=status.HTTP_400_BAD_REQUEST) 

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_my_personal_details(request):
      username = request.data.get('username',"")
      if  username == "" or username is None:
            pass
      else:
            if len(username.strip())<6:
                  return Response({"message":"Username should contain at least 6 characters.."},
                              status=400)
            elif User.objects.filter(username = username).exclude(id=request.user.id).count()>0:
                  return Response({"message":"Username already in use."},status=400)
      user = User.objects.get(id=request.user.id)
      user_details = UserDetail.objects.get(user_id=request.user.id)
      user.first_name=request.data.get('first_name',user.first_name)
      user.last_name=request.data.get('last_name',user.last_name)
      user.username=request.data.get('username',user.username)
      user.save()
      user_details.gender_id=request.data.get('gender',user_details.gender_id)
      user_details.birth_date=request.data.get('birth_date',user_details.birth_date)
      user_details.about=request.data.get('about',user_details.about)
      user_details.image=request.data.get('image',user_details.image)
      user_details.zip_code=request.data.get('zip_code',user_details.zip_code)
      user_details.city_id=request.data.get('city',user_details.city_id)
      user_details.brands=request.data.get('brands',user_details.brands)
      user_details.city_longitude=request.data.get('city_longitude',user_details.city_longitude)
      user_details.city_latitude=request.data.get('city_latitude',user_details.city_latitude)
      user_details.address=request.data.get('address',user_details.address)
      user_details.address_longitude=request.data.get('address_longitude',user_details.address_longitude)
      user_details.address_latitude=request.data.get('address_latitude',user_details.address_latitude)
      user_details.save()

      return Response({"message":"OK"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me_master(request):
      return Response(MasterSerializer(UserDetail.objects.get(user=request.user,user_role__code="CL",
      is_master=True)).data,
                              status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me_client(request):
      return Response(ClientDetailSerializer(UserDetail.objects.get(user=request.user,
      user_role__code="CL",is_client=True)).data,
                              status=status.HTTP_200_OK)

@api_view(['POST'])
def send_forget_code_phone(request):
      phone_number=request.data['phone_number']
      # send_password = request.data['send_password']
      try:
            user_details = UserDetail.objects.get(phone_number=phone_number)
            try:
                  ConfirmCode.objects.filter(phone_number=phone_number).delete()
            finally:
                  code = randint(100000, 999999)
                  ConfirmCode(phone_number=phone_number,code=code).save()
                  # send_credental(User.objects.get(id=user_details.user_id),send_password, to_email=False,
                  # request=request, to_phonenumber=phone_number)
                  return Response({"message":"OK"},status=status.HTTP_201_CREATED)
      except:
            return Response({"message":"No user with this phone number registered."},
                              status=status.HTTP_404_NOT_FOUND) 

@api_view(['POST'])
def send_forget_code_email(request):
      email=request.data['email']
      try:
            User.objects.get(email=email)
            try:
                  ConfirmCode.objects.filter(email=email).delete()
            finally:
                  code =randint(100000, 999999)
                  ConfirmCode(email=email,code=code).save()
                  send_email(to_email=email,
                              code="RECCR",
                             code_email=str(code),
                             lang=request.GET.get("lang",None))
                  
                  return Response({"message":"OK"},status=status.HTTP_201_CREATED)
      except:
            return Response({"message":"No user with this email registered."},
                              status=status.HTTP_404_NOT_FOUND) 

def send_credental(user,send_password, to_email, request, to_phonenumber):
      if to_email:
            if send_password:
                  new_password = "12345678"
                  user.set_password(new_password)
                  user.save()
                  send_email(to_email=user.email,
                             code="SPSWD",
                             password=new_password)
            else:
                  send_email(to_email=user.email,
                             code="SUSRN",
                             user_name=user.username)
      else:
            lang = "fr"
            try:
                  lang=request.data['lang']
            except:
                  pass
            if send_password:
                  new_password = "12345678"
                  user.set_password(new_password)
                  user.save()
                  nt = NotificationType.objects.get(code="SNPWPSMS")
                  body = nt.text_fr if lang=="fr" else nt.text_en
                  body = str(body).replace("<<PASSWORD<<",str(new_password))
            else:
                  pass
                  nt = NotificationType.objects.get(code="SUWUSMS")
                  body = nt.text_fr if lang=="fr" else nt.text_en
                  body = str(body).replace("<<USERNAME<<",str(user.username))
            send_sms(body=body, phonenumber=to_phonenumber)

@api_view(['POST'])
def check_forget_code_phone(request):
      phone_number=request.data['phone_number']
      confirm_code=request.data['confirm_code']
      send_password = randint(10000000, 99999999)
      try:
            user_details = UserDetail.objects.get(phone_number=phone_number)
            try:
                  conf_code=ConfirmCode.objects.get(phone_number=phone_number,code=confirm_code)
                  conf_code.delete()
                  send_credental(User.objects.get(id=user_details.user_id),send_password, to_email=False,
                                                                   request=request, to_phonenumber=phone_number)
                  return Response({"message":"OK"},status=status.HTTP_200_OK)

            except:
                  return Response({"message":"Not found"},
                                          status=status.HTTP_404_NOT_FOUND) 
      except:
            return Response({"message":"No user with this phone number."},
                                          status=status.HTTP_404_NOT_FOUND) 

@api_view(['POST'])
def check_forget_code_email(request):
      email=request.data['email']
      confirm_code=request.data['confirm_code']
      send_password = randint(10000000, 99999999)
      try:
            user = User.objects.get(email=email)
            try:
                  conf_code=ConfirmCode.objects.get(email=email,code=confirm_code)
                  conf_code.delete()
                  send_credental(User.objects.get(id=user.id),send_password, to_email=user.email,
                                                                   request=request, to_phonenumber=False)
                  return Response({"message":"OK"},status=status.HTTP_200_OK) 
            except:
                  return Response({"message":"Not found"},
                                          status=status.HTTP_404_NOT_FOUND) 
      except:
            return Response({"message":"No user with this email."},
                                          status=status.HTTP_404_NOT_FOUND) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def remove_my_profile(request):
      user_details = UserDetail.objects.get(user_id=request.user.id)
      user_details.is_removed=True
      
      user_details.save()
      user = User.objects.get(id=request.user.id)
      user.is_active = False
      user.save()
      return Response({"message":"OK"},status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def unremove_user_profile(request,pk):
      userdetails = UserDetail.objects.get(id=pk)
      userdetails.is_removed=False
      userdetails.save()
      user = User.objects.get(id=userdetails.user.id)
      user.is_active = True
      user.save()
      return Response({"message":"OK"},status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_change_email_code(request):
      email=request.data['email']
      if  User.objects.filter(email=email).count()>0:
            return Response({"message":"Email already in use."},
                                    status=status.HTTP_400_BAD_REQUEST)
      try:
            ConfirmCode.objects.filter(email=email).delete()
      finally:
            code = 111111
            ConfirmCode(email=email,code=code).save()
            send_email(to_email=email,
                             code="CHEM",
                             lang=request.GET.get("lang",None))
            return Response({"message":"OK"},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_change_phone_code(request):
      phone_number=request.data['phone_number']
      if  UserDetail.objects.filter(phone_number=phone_number).count()>0:
            return Response({"message":"Phone number already in use."},
                                    status=status.HTTP_400_BAD_REQUEST)
      try:
            ConfirmCode.objects.filter(phone_number=phone_number).delete()
      finally:
            ConfirmCode(phone_number=phone_number,code=111111).save()
            return Response({"message":"OK"},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_change_email_code_email(request):
      email=request.data['email']
      confirm_code=request.data['confirm_code']
      user = User.objects.get(id=request.user.id)
      try:
            conf_code=ConfirmCode.objects.get(email=email,code=confirm_code)
            conf_code.delete()
            user.email = email
            user.save()
            return Response({"message":"OK"},status=status.HTTP_200_OK) 
      except:
            return Response({"message":"Not found"},
                                    status=status.HTTP_404_NOT_FOUND) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_change_phone_number_code_email(request):
      phone_number=request.data['phone_number']
      confirm_code=request.data['confirm_code']
      user = UserDetail.objects.get(user_id=request.user.id)
      try:
            conf_code=ConfirmCode.objects.get(phone_number=phone_number,code=confirm_code)
            conf_code.delete()
            user.phone_number = phone_number
            user.save()
            
            return Response({"message":"OK"},status=status.HTTP_200_OK) 
      except:
            return Response({"message":"Not found"},
                                    status=status.HTTP_404_NOT_FOUND) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_tarif(request,pk):
      stripe.api_key = General.objects.all().first().stripe_key_for_master
      user = UserDetail.objects.get(user_id=request.user.id)
      tarif = Tarif.objects.get(id=pk)
      try:
            mts = MasterTarifSubscribtion.objects.get(user_id=user.id,tarif=tarif)   
      except:
            mts = MasterTarifSubscribtion(user_id=user.id,
                              tarif=tarif,
                              payed=False,
                              expire_date=datetime.datetime.now()+relativedelta(months=tarif.month))
      mts.save()
      customer = stripe.Customer.create()        
 
      payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                  "number":request.data['number'],
                  "exp_year":request.data['exp_year'],
                  "exp_month":request.data['exp_month'],
                  "cvc":request.data['cvc'],
            })
      payment_intent = stripe.PaymentIntent.create(
            amount=int(tarif.price*100),
            currency="eur",
            payment_method=payment_method,
            payment_method_types=["card"],
            customer=customer['id'],
            payment_method_options={
                  "card":{
                        "request_three_d_secure":"automatic"
                        }
                  })
      obj = stripe.PaymentIntent.confirm(
            payment_intent['id'],
            return_url="{0}://{1}".format('https', str(request.get_host())) + "/userdetails/check-tarif-payment/"+str(payment_intent.id)+"/?rurl="+str(request.GET.get("rurl"))
      )
      transaction = Transaction(master_tarif_subscription=mts, 
                                    user_id=user.id, 
                                    price=tarif.price,
                                    payment_id = payment_intent['id'],
                                    status="pending")
      transaction.save()
      if obj['status'] == "succeeded":
            return Response({"ok":True,"id":obj['id']})
      else:
            return Response({"iframe_url":obj['next_action']['redirect_to_url']['url']},status=200)

@api_view(['GET'])
def check_tarif_payment(request, id):
      stripe.api_key = General.objects.all().first().stripe_key_for_master
      transaction = Transaction.objects.get(payment_id=id)
      master_tarif_subscription = MasterTarifSubscribtion.objects.get(
                                    id=transaction.master_tarif_subscription_id)
      if stripe.PaymentIntent.retrieve(id)['status'] == "succeeded":
            master_tarif_subscription.expire_date=datetime.datetime.now()+relativedelta(months=+master_tarif_subscription.tarif.month) 
            master_tarif_subscription.payed=True
            master_tarif_subscription.save()
            transaction.status="succeed"
            transaction.save()
            if request.GET.get("rurl") is None:
                  return Response({"ok":True})
            return CustomRedirect(request.GET.get("rurl"))
      else:
            if master_tarif_subscription.payed == True:
                  transaction.delete()
            else:
                  transaction.delete()
                  master_tarif_subscription.delete()
            if request.GET.get("rurl") is None:
                  return Response({"ok":False}) 
            return CustomRedirect(request.GET.get("rurl"))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_joined_user_statistic(request):
      start_date =datetime.datetime.strptime(request.data['start_date'], '%Y-%m-%d')
      end_date =datetime.datetime.strptime(request.data['end_date'], '%Y-%m-%d')
      users = UserDetail.objects.filter(user__date_joined__gte=start_date).filter(
                              user__date_joined__lte=end_date
                        ).filter(user_role__code=request.data['role'])
      return Response(users.count())

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_popular_masters(request):
      limit = int(request.GET.get('limit'))
      masters = UserDetail.objects.filter(user_role__code="CL",
                                                is_master=True,
                                                user__is_active=True
                                          ).annotate(raiting_sum = Avg('my_reviews__rating')
                                          ).order_by("-raiting_sum")[:limit+10]
      result = [{
                  "full_name":master.user.first_name+" "+master.user.last_name,
                  "image":master.image,
                  "id":master.id,
                  "rating":master.rating
            } for master in masters if master.rating>0]
      final=[]
      if len(result) > limit:
            final = result[:limit]
      else:
            final = result
            for master in masters:
                  if master.rating==0:
                        if len(final)==limit:
                              break
                        else:
                              final.append({
                                          "full_name":master.user.first_name+" "+master.user.last_name,
                                          "image":master.image,
                                          "id":master.id,
                                          "rating":master.rating})
            
      return Response(final,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stripe_account(request):
      user_details = UserDetail.objects.get(user_id=request.user.id)
      if user_details.stripe_client_id is not None and  user_details.stripe_client_id != "":
            stripe_account = stripe.Account.retrieve(user_details.stripe_client_id)
            obj = {
                  "external_accounts":stripe_account['external_accounts']
            }
            return Response(obj,status=200)
      else:
            return Response({"message":"Stripe account doesn't exists."},status=400)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def activate_inactvate_user(request):
      user_id = request.GET.get("user_id")
      user = UserDetail.objects.get(id=user_id)
      us = User.objects.get(id=user.user_id)
      us.is_active = not us.is_active
      us.save()
      old_token = Token.objects.get(user=us)
      old_token.delete()
      Token.objects.create(user=us)
      return Response({"message":"OK"},status=200)

