from timeline.serializers import  ReviewSerializer
from utils.serializers import ServiceSerializer
from userdetails.serializers import UserDetailSerializer
from rest_framework import serializers
from .models import Order, Transaction
import service 

class OrderSerializer(serializers.ModelSerializer):
    user=UserDetailSerializer()
    master=UserDetailSerializer()
    service=ServiceSerializer()

    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["event"] = service.get_event_by_id(calendar_id=instance.google_calendar_id,
                                          event_id=instance.google_event_id)
        data['reviews'] = ReviewSerializer(instance.order_reviews.all(),many=True).data
        return data

class OrderSmallSerializer(serializers.ModelSerializer):
    master=UserDetailSerializer()
    service=ServiceSerializer()

    class Meta:
        model = Order
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):
    order = OrderSmallSerializer()
    class Meta:
        model = Transaction
        fields = "__all__"
