from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from django.urls import path

from files import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'files', views.FileViewSet)
router.register(r'files-object', views.FileObjectViewSet)
urlpatterns = [
    url(r'^', include(router.urls)),
]