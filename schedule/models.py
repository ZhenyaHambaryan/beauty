from userdetails.models import UserDetail
from django.db import models
from utils.models import Service
from simple_history.models import HistoricalRecords

class Order(models.Model):
      user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="user_orders")
      master = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="master_orders")
      service = models.ForeignKey(Service, on_delete=models.CASCADE,null=False)
      minutes = models.PositiveIntegerField(null=True,blank=True)
      start_date = models.DateTimeField(null=True, blank=True)
      end_date = models.DateTimeField(null=True, blank=True)
      price = models.FloatField(null=True,blank=True)
      go_home = models.BooleanField(default=False)
      comment = models.CharField(max_length=1000, null=True, blank=True)
      google_calendar_id = models.CharField(max_length=500, null=True, blank=True)
      google_event_id = models.CharField(max_length=500, null=True, blank=True)
      status = models.CharField(max_length=255, null=True, blank=True)
      is_prepayed = models.BooleanField(default=False)
      prepayed_price = models.FloatField(null=True,blank=True)
      prepayed_status = models.CharField(max_length=255, null=True, blank=True, default="pending")
      cancel_reason = models.CharField(max_length=1000, null=True, blank=True)
      created_at = models.DateTimeField(auto_now_add=True)
      payment_status = models.CharField(max_length=255, null=True, blank=True, default="pending")
      payed_by_cache = models.BooleanField(default=True) 
      
class Transaction(models.Model):
      amount = models.FloatField(null=True)
      payment_id = models.CharField(null=True,max_length=1000,blank=True)
      date = models.DateTimeField(auto_now_add=True)
      status = models.CharField(max_length=255,null=True,blank=True,default="pending")
      client = models.ForeignKey(UserDetail,null=True,on_delete=models.CASCADE,blank=False,
                                          related_name="client_transactions")
      master = models.ForeignKey(UserDetail,null=True,on_delete=models.CASCADE,blank=False,
                                          related_name="master_transactions")
      order = models.ForeignKey(Order,null=True,on_delete=models.CASCADE,blank=False)
      refunded_amount = models.FloatField(null=True,default=0,blank=True)

      history = HistoricalRecords()
      
      def __str__(self):
            return str(self.amount)

