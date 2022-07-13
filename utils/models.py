from django.db import models
from django.db.models.deletion import PROTECT

class UserRole(models.Model):
      title = models.CharField(max_length=255, blank=True, null=False)
      code = models.CharField(max_length=5, blank=True, null=False)

      def __str__(self):
            return self.title

class Language(models.Model):
      title = models.CharField(max_length=255, blank=True, null=False)
      code = models.CharField(max_length=5, blank=True, null=False)

      def __str__(self):
            return self.title

class Gender(models.Model):
      name_en = models.CharField(max_length=255, blank=True, null=False)
      name_fr = models.CharField(max_length=255, blank=True, null=False)

      def __str__(self):
            return self.name_en

class Category(models.Model):
      name_en = models.CharField(max_length=255, blank=True, null=False)
      name_fr = models.CharField(max_length=255, blank=True, null=False)
      icon = models.CharField(max_length=1000, blank=True, null=False)

      def __str__(self):
            return self.name_en

class Service(models.Model):
      category = models.ForeignKey(Category,on_delete=models.CASCADE,null=False,blank=False,
                                    related_name="services")
      name_en = models.CharField(max_length=255, blank=True, null=False)
      name_fr = models.CharField(max_length=255, blank=True, null=False)
      icon = models.CharField(max_length=1000, blank=True, null=False)
      is_popular = models.BooleanField(default=False) 
      slug = models.CharField(max_length=255, blank=True, null=True)

      def __str__(self):
            return self.name_en

class Tarif(models.Model):
      title_en = models.CharField(max_length=255, blank=True, null=True)
      title_fr = models.CharField(max_length=255, blank=True, null=True)
      description_en = models.CharField(max_length=1000, blank=True, null=True)
      description_fr = models.CharField(max_length=1000, blank=True, null=True)
      image = models.CharField(max_length=1000, blank=True, null=True)
      month = models.IntegerField(default=1)
      price = models.DecimalField(default=1,null=False,max_digits=50,decimal_places=2)
      category_count = models.PositiveIntegerField(default=1)
      is_active = models.BooleanField(default=True)
      is_deleted = models.BooleanField(default=False)
      
      def __str__(self):
            return self.title_en

class Country(models.Model):
      title_en = models.CharField(max_length=255, blank=True, null=True)
      title_fr = models.CharField(max_length=255, blank=True, null=True)
      code = models.CharField(max_length=255, blank=True, null=True)

      def __str__(self):
            return self.title_en

class Departement(models.Model):
      country = models.ForeignKey(Country,on_delete=PROTECT,null=False, blank=False)
      title_en = models.CharField(max_length=255, blank=True, null=True)
      title_fr = models.CharField(max_length=255, blank=True, null=True)
      number = models.CharField(max_length=255, null=True, blank=True)
      def __str__(self):
            return self.title_en

class City(models.Model):
      country = models.ForeignKey(Country,on_delete=PROTECT,null=False, blank=False)
      departement = models.ForeignKey(Departement,on_delete=PROTECT,null=True, blank=True)
      title_en = models.CharField(max_length=255, blank=True, null=True)
      title_fr = models.CharField(max_length=255, blank=True, null=True)
      logitude = models.CharField(max_length=255, blank=True, null=True)
      latitude = models.CharField(max_length=255, blank=True, null=True)
      slug = models.CharField(max_length=255, blank=True, null=True)



      def __str__(self):
            return self.title_en

class Feedback(models.Model):
      name = models.CharField(max_length=255, blank=False, null=False)
      phone_number = models.CharField(max_length=255, blank=False, null=False)
      email = models.EmailField(max_length=255, blank=False, null=False)
      message = models.TextField(blank=False, null=False)
      is_seen = models.BooleanField(default=False)
      created_at = models.DateTimeField(auto_now_add=True)
      def __str__(self):
            return self.message

class AboutUs(models.Model):
      title_en = models.CharField(max_length=255, blank=False, null=False)
      title_fr = models.CharField(max_length=255, blank=False, null=False)
      description_en = models.TextField(blank=False, null=False)
      description_fr = models.TextField(blank=False, null=False)
      is_active = models.BooleanField(default=True)
      image = models.CharField(max_length=255, null=True, blank=True)
      order = models.IntegerField(default=1)
      created_at = models.DateTimeField(auto_now_add=True)
      def __str__(self):
            return self.title_en

class General(models.Model):
      radius = models.IntegerField()
      stripe_key_for_master = models.CharField(null=True, blank=True, max_length=500)
      application_fee =  models.IntegerField(default=10)
      def __str__(self):
            return str(self.radius)
