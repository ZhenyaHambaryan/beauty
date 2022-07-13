from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    path('joined-user/',views.get_joined_user),
    path('post/',views.get_post),
    path('post-comment/',views.get_post_comment),
    path('order/',views.get_order),
    path('master-service/',views.get_master_service),
]
