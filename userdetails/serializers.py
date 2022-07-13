from django.contrib.auth.models import User
from django.db.models.aggregates import Avg, Count, Sum
from django.db.models.query_utils import Q
from rest_framework import serializers
from utils.serializers import CategoryDetailsSerializer, CitySerializer, LanguageSerializer, TarifSerializer, UserRoleSerializer
from .models import (FavoriteMasters, MasterService, MasterTarifSubscribtion, UserCategory, 
                    UserDetail, 
                    MasterCertificate, 
                    MasterWorkPhoto, 
                    Settings,
                    HelpMessage
                    )
from utils.serializers import ServiceSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','is_active')

class UserDetailSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    user_role=UserRoleSerializer()
    class Meta:
        model = UserDetail
        fields = "__all__"
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["rating"] = instance.rating
        data["city_details"] = CitySerializer(instance.city).data
        return data

class ClientDetailSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    user_role=UserRoleSerializer()
    
    class Meta:
        model = UserDetail
        fields = '__all__'
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["rating"] = instance.rating
        data["city_details"] = CitySerializer(instance.city).data
        return data

class MasterServiceSerializer(serializers.ModelSerializer):
    service=ServiceSerializer(read_only=True)
    class Meta:
        model =MasterService
        fields = '__all__'

class MasterService2Serializer(serializers.ModelSerializer):
    class Meta:
        model =MasterService
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['service_details'] = ServiceSerializer(instance.service).data
        return data
    
class MasterServiceDetailSerializer(serializers.ModelSerializer):
    service_details=ServiceSerializer(source='service',read_only=True)
    user_details=UserDetailSerializer(source='user',read_only=True)
    class Meta:
        model =MasterService
        fields = ['id',
                    'user',
                    'service',
                    'subtitle',
                    'user_details',
                    'service_details',
                    'minutes',
                    'price',
                    'go_home',
                    'go_home_price',
                    'prepay_percent',
                    'created_at'
                    ]

class MasterCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterCertificate
        fields = "__all__"

class MasterWorkPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterWorkPhoto
        fields = "__all__"

class MasterSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    city_details = CitySerializer(source="city",read_only=True)
    master_services=MasterServiceSerializer(many=True, read_only=True)
    master_certificates=MasterCertificateSerializer(many=True, read_only=True)
    master_work_photo=MasterWorkPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserDetail
        fields = ('id','user','phone_number','image',
                'city','city_details','city_longitude','city_latitude','brands',
                'address','address_longitude','address_latitude','about',
                'master_certificates','master_services','master_work_photo','google_calendar_id',
                'rating','price_sum',"is_client","is_master",'review_count','posts_count',
                'is_popular','stripe_customer_id','stripe_client_id','is_removed')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['service_name'] = {
                    "name_en":"",
                    "name_fr":""
                }
        if instance.master_services.all().count()>0:
                data['service_name']['name_en'] = instance.master_services.all().first().service.name_en
                data['service_name']['name_fr'] = instance.master_services.all().first().service.name_fr
        data["rating"] = instance.rating
        data['review_count']=instance.my_reviews.count()
        data['done_order_count']=instance.master_orders.filter(Q(status='done') | Q(status="passed")).count()
        data['repeated_client_count'] = instance.master_orders.filter(
                                Q(status='done') | Q(status="passed")).values('user').annotate(count = Count("user")
                                ).aggregate(user_count = Count('user',filter=Q(count__gt=1)))['user_count']
        return data

class MasterSearchSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    is_favorite = serializers.BooleanField(read_only=True)
    class Meta:
        model = UserDetail
        fields = ('id','user','phone_number','image','city','city_longitude','city_latitude',
                'brands','address','address_longitude','address_latitude',
                'about','rating','review_count','is_favorite','is_popular')
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['master_services'] = MasterServiceSerializer(instance.master_services,many=True).data
        data['city'] = CitySerializer(instance.city).data

        data['service_name'] = {
                    "name_en":"",
                    "name_fr":""
                }
        if instance.master_services.all().count()>0:
                data['service_name']['name_en'] = instance.master_services.all().first().service.name_en
                data['service_name']['name_fr'] = instance.master_services.all().first().service.name_fr
        return data

class SettingsSerializer(serializers.ModelSerializer):
    language_details = LanguageSerializer(source="language",read_only=True)
    class Meta:
        model = Settings
        fields = ("id",'user','language','language_details','push_notification','geolocation')

class HelpMessageSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(source="user",read_only=True)
    class Meta:
        model = HelpMessage
        fields = ("id",'user','user_details','message','created_at','is_answered','answered_at')

class UserSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ['image','is_master']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id']=instance.id
        data['first_name']=instance.user.first_name
        data['last_name']=instance.user.last_name
        data['username']=instance.user.username
        data['service_name'] = {
            "name_en":"",
            "name_fr":""
        }
        if instance.master_services.all().count()>0:
            data['service_name']['name_en'] = instance.master_services.all().first().service.name_en
            data['service_name']['name_fr'] = instance.master_services.all().first().service.name_fr
        return data
    
class UserCategorySerializer(serializers.ModelSerializer):
    category_details = CategoryDetailsSerializer(source="category",read_only=True)
    class Meta:
        model = UserCategory
        fields = ['id','user','category','category_details']
 
class MasterTarifSubscribtionSerializer(serializers.ModelSerializer):
    tarif_details = TarifSerializer(source="tarif",read_only=True)
    user_details = UserDetailSerializer(source="user",read_only=True)
    class Meta:
        model = MasterTarifSubscribtion
        fields = ['id',
                    'user',
                    'user_details',
                    'tarif',
                    'tarif_details',
                    'expire_date',
                    'created_at',
                    'payed'
                ]
class FavoriteMastersSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteMasters
        fields = "__all__"
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["master"] = UserDetailSerializer(instance.master).data
        return data
