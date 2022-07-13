from django.urls import path
from django.conf.urls import include, url
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'scheduled-email', views.ScheduledEmailViewSet)
router.register(r'scheduled-notification', views.ScheduledNotificationViewSet)
router.register(r'notification', views.NotificationViewSet)
router.register(r'notification-type', views.NotificationTypeViewSet)
router.register(r'email-type', views.EmailTypesViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('get-unseen-notification-count/',views.get_unseen_notifications_count),
    path('add-push-token/',views.add_push_token),
    path('remove-push-token/',views.remove_push_token),
]
