from django.urls import path
from . import views

urlpatterns = [
    path('get-room-for-admin/<int:pk>/', views.get_room_for_admin),
    path('get-room-for-client/', views.get_room_for_user),
    path('get-unseen-message-room-count-user/', views.get_unseen_message_count_user),
    path('set-message-seen/<int:pk>/', views.set_message_seen),
    path('test/', views.test),
]
