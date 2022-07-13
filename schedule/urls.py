from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from django.urls import path

from . import cron
from . import views

router = DefaultRouter()
router.register(r'order', views.OrderViewSet)
router.register(r'transaction', views.TransactionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('get-client-orders/<int:pk>/',views.get_client_orders),
    path('get-master-orders/',views.get_master_orders),

    path('create-non-working-date/',views.create_non_working_date),
    path('create-busy-event/',views.create_busy_event),
    path('create-working-event/',views.create_working_event),
    path('update-working-event/<slug:eid>/',views.update_working_event),
    path('delete-working-event/',views.delete_working_event),

    path('create-order/',views.create_order),
    path('cancel-order/<int:pk>/',views.cancel_order),
    path('done-order/<int:pk>/',views.done_order),
    path('accept-order/<int:pk>/',views.accept_order),
    path('get-pending-order-count/<int:pk>/',views.get_pending_order_count),

    path('check-payment/<slug:id>/<int:pk>/',views.check_payment),
    path('stripe-login/',views.stripe_login),
    path('check-stripe/<int:pk>/<slug:id>/', views.check_stripe),

    path('create-card/', views.create_card),
    path('get-cards/', views.get_cards),
    path('remove-card/', views.remove_card),

    path('get-calendar-by-date/', views.get_calendar_by_date),
    path('get-monthly-orders/', views.get_monthly_orders),

    path('get-client-masters/<int:pk>/', views.get_client_masters),
    path('get-master-clients/<int:pk>/', views.get_master_clients),

    path('get-daily-schedule-by-service/', views.get_daily_schedule_by_service),

    path('pay-for-order/<int:pk>/',views.pay_for_order),
    path('check-full-payment/<slug:id>/<int:pk>/',views.check_full_payment),
    path('get-my-working-events/',views.get_my_working_events),
    path('delete-non-working-day/',views.delete_non_working_day),

    path('delete/',views.delete),
    
    path('check-service-availability/<int:pk>/',views.check_service_availability),
    path('payment-intent-to-costumer/',views.payment_intent_to_costumer),
]
