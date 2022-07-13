from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from django.urls import path
from utils import views

router = DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'service', views.ServiceViewSet,basename="service")
router.register(r'gender', views.GenderViewSet)
router.register(r'language', views.LanguageViewSet)
router.register(r'tarif', views.TarifViewSet)
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'country', views.CountryViewSet)
router.register(r'city', views.CityViewSet)
router.register(r'about-us', views.AboutUsViewSet)
router.register(r'general', views.GeneralViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('get-popular-services/',views.get_popular_services),
    path('set-feedback-seen/<int:pk>/',views.set_feedback_seen),
    path('activate-deactivate-tarif/<int:pk>/',views.activate_deactivate_tarif),
    path('upload-departements/',views.upload_departements),
    path('upload-cities/',views.upload_cities),
]

