from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, PROTECT
from utils.models import Category, City, Tarif, UserRole, Gender,  Service, Language
from django.db.models.aggregates import Avg, Sum
from django.db.models import Sum

class UserDetail(models.Model):
      user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_details")
      phone_number = models.CharField(null=True,blank=True,max_length=255)
      user_role = models.ForeignKey(UserRole,on_delete=models.SET_NULL,blank=True,null=True)
      gender = models.ForeignKey(Gender,on_delete=models.SET_NULL,blank=True,null=True)
      birth_date = models.DateField(null=True, blank=True)
      about = models.CharField(null=True,blank=True,max_length=1000)
      brands = models.CharField(null=True,blank=True,max_length=1000)
      image = models.CharField(null=True,blank=True,max_length=2000)
      zip_code = models.CharField(null=True,blank=True,max_length=255)
      city = models.ForeignKey(City,null=True,blank=True, 
                                    on_delete=PROTECT, related_name="city_masters")
      city_longitude = models.CharField(null=True,blank=True,max_length=255)
      city_latitude = models.CharField(null=True,blank=True,max_length=255)
      address = models.CharField(null=True,blank=True,max_length=1000)
      address_longitude = models.CharField(null=True,blank=True,max_length=255)
      address_latitude = models.CharField(null=True,blank=True,max_length=255)
      is_removed = models.BooleanField(default=False)
      google_calendar_id = models.CharField(max_length=500, null=True, blank=True)
      stripe_customer_id = models.CharField(max_length=500, null=True, blank=True)
      stripe_client_id = models.CharField(max_length=500, null=True, blank=True)
      created_at = models.DateTimeField(auto_now_add=True)
      is_client = models.BooleanField(default=True)
      is_master = models.BooleanField(default=False)
      is_popular = models.BooleanField(default=False)
      
      def __str__(self):
            return self.user.first_name+" " + self.user.last_name

      @property
      def rating(self):
            rating = self.my_reviews.all().aggregate(raiting_sum=Avg('rating'))['raiting_sum']
            if rating is not None:
                  return round(rating)
            else:
                  return 0
      @property
      def review_count(self):
            return self.my_reviews.all().count()
      @property
      def posts_count(self):
            return self.user_posts.all().count()

      @property
      def price_sum(self):
            rating = self.master_orders.filter(status="done").aggregate(price_sum=Sum('price'))['price_sum']
            if rating is not None:
                  return round(rating,1)
            else:
                  return 0

class MasterCertificate(models.Model):
      user = models.ForeignKey(UserDetail,on_delete=models.CASCADE,blank=False,null=False,
                                    related_name="master_certificates")
      image = models.CharField(null=True,blank=True,max_length=2000)
      created_at = models.DateTimeField(auto_now_add=True) 

class MasterWorkPhoto(models.Model):
      user = models.ForeignKey(UserDetail,on_delete=models.CASCADE,blank=False,null=False,
                                    related_name="master_work_photo")
      image = models.CharField(null=True,blank=True,max_length=2000)
      created_at = models.DateTimeField(auto_now_add=True) 

class MasterService(models.Model):
      user = models.ForeignKey(UserDetail,on_delete=models.CASCADE,blank=False,null=False,
                              related_name="master_services")
      subtitle = models.CharField(max_length=255, null=True, blank=True)
      service = models.ForeignKey(Service,on_delete=models.CASCADE,blank=False,null=False)
      minutes = models.PositiveIntegerField(null=True,blank=True)
      price = models.DecimalField(null=True,blank=True, decimal_places=2,max_digits=25)
      go_home = models.BooleanField(default=False)
      go_home_price = models.DecimalField(null=True,blank=True, decimal_places=2,max_digits=25)
      prepay_percent = models.FloatField(null=True,blank=True)
      created_at = models.DateTimeField(auto_now_add=True) 
      class Meta:
            unique_together = ('user', 'service',)

class ConfirmCode(models.Model):
      phone_number = models.CharField(max_length=255, blank=True, null=True)
      email = models.CharField(max_length=255, blank=True, null=True)
      code = models.CharField(max_length=255, blank=True, null=False)
      created_at = models.DateTimeField(auto_now_add=True)

class Settings(models.Model):
      user = models.ForeignKey(UserDetail,on_delete=models.CASCADE,blank=False,null=False,
                  related_name="settings")
      language = models.ForeignKey(Language,on_delete=models.SET_NULL,blank=True,null=True)
      push_notification=models.BooleanField(null=True,blank=True,default=False)
      geolocation=models.BooleanField(null=True,blank=True,default=False)

      def __str__(self):
            return self.language.title

class HelpMessage(models.Model):
      user = models.ForeignKey(UserDetail,on_delete=models.CASCADE,blank=False,null=False,
                  related_name="user_help_messages")
      message = models.TextField(null=False,blank=False)
      created_at = models.DateTimeField(auto_now_add=True)
      is_answered = models.BooleanField(null=True,blank=True,default=False)
      answered_at = models.DateTimeField(blank=True, null=True)
      
      def __str__(self):
            return self.message

class MasterTarifSubscribtion(models.Model):
      user = models.ForeignKey(UserDetail,on_delete=models.CASCADE,blank=False,null=False,
                              related_name="master_subscribed_category")
      tarif = models.ForeignKey(Tarif,on_delete=models.PROTECT,blank=False,null=False, related_name="tarif_users")
      expire_date = models.DateTimeField()
      created_at = models.DateTimeField(auto_now_add=True)
      payed = models.BooleanField(default=False)

class UserCategory(models.Model):
      user = models.ForeignKey(UserDetail,on_delete=CASCADE, null=False, blank=False)
      category = models.ForeignKey(Category,on_delete=models.CASCADE,blank=False,null=False)
      created_at = models.DateTimeField(auto_now_add=True)
      class Meta:
            unique_together = ('user','category')

class Transaction(models.Model):
      master_tarif_subscription = models.ForeignKey(MasterTarifSubscribtion,on_delete=models.PROTECT,blank=False,null=False)
      user = models.ForeignKey(UserDetail,on_delete=models.PROTECT,blank=False,null=False)
      price = models.PositiveIntegerField(null=True)
      status= models.CharField(null=True,max_length=255)
      transaction_id = models.CharField(null=True,max_length=255)
      created_date = models.DateTimeField(auto_now_add=True)
      payment_id  =models.CharField(null=True, blank=True,max_length=255)

class FavoriteMasters(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False, 
                                                blank=False, related_name="favorite_masters")
      master = models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False, 
                                                blank=False, related_name="master_favorite_users")
      created_at = models.DateTimeField(auto_now_add=True)

