from datetime import datetime, timedelta 
from django.db.models.query_utils import Q
from schedule.models import Order
from schedule.views import send_done_push

def change_passed_status():
      date = datetime.now()
      orders = Order.objects.filter(Q(Q(status="pending") | Q(status="accepted"))
                                    & Q(end_date__lte=date))
      for order in orders:
            order.status="passed"
            send_done_push(order_id=order.id)
            order.save()
