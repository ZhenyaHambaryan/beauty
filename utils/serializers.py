from rest_framework import serializers
from .models import (AboutUs, Category, City, Country, Departement, Feedback, General, 
                                Service, Gender, Tarif, UserRole,Language)

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class ServiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    services=ServiceDetailSerializer(read_only=True,many=True)
    class Meta:
        model = Category
        fields = '__all__'

class Category2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    category_details=CategoryDetailsSerializer(source="category",read_only=True)
    class Meta:
        model = Service
        fields =[
            "id","category",
                    "name_en",
                    "name_fr",
                    "icon",
                    "is_popular",
                    "category_details"
                    ]
                    
class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'

class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'

class GeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = General
        fields = '__all__'

class DepartementSerializer(serializers.ModelSerializer):
    country_details = CountrySerializer(source="country",read_only=True)
    class Meta:
        model = Departement
        fields = ('id','country','country_details','title_en','title_fr')

class CitySerializer(serializers.ModelSerializer):
    country_details = CountrySerializer(source="country",read_only=True)
    departement_details = DepartementSerializer(source = "departement",read_only=True)
    class Meta:
        model = City
        fields = ('id','country','country_details',
                  'title_en','title_fr',
                  "departement_details",
                  "departement",
                  'logitude','latitude','slug',)

