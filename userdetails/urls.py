from django.urls import path
from django.conf.urls import include, url
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', views.UserDetailViewSet)
router.register(r'master-certificate', views.MasterCertificateViewSet)
router.register(r'master-work-photo', views.MasterWorkPhotoViewSet)
router.register(r'master-service', views.MasterServiceViewSet,basename = "master-service")
router.register(r'settings', views.SettingsViewSet)
router.register(r'help-message', views.HelpMessageViewSet)
router.register(r'master-tarif-subscribtion', views.MasterTarifSubscribtionViewSet)
router.register(r'user-category', views.UserCategoryViewSet)
router.register(r'master', views.MasterViewSet,basename = "master")
router.register(r'favorite-masters', views.FavoriteMastersViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('send-registration-code/', views.send_registration_code),
    path('register-user/', views.register_user),
    path('set-my-role/', views.set_my_role),
    path('login-user/', views.user_login),
    path('send-forget-code-phone/', views.send_forget_code_phone),
    path('send-forget-code-email/', views.send_forget_code_email),
    path('check-forget-code-phone/', views.check_forget_code_phone),
    path('check-forget-code-email/', views.check_forget_code_email),
    path('edit-my-personal-details/', views.edit_my_personal_details),
    path('get-me-master/', views.get_me_master),
    path('get-me-client/', views.get_me_client),
    path('remove-my-profile/', views.remove_my_profile),
    path('unremove-user-profile/<int:pk>/', views.unremove_user_profile),
    path('email-unique-validation/', views.email_unique_validation),
    path('username-unique-validation/', views.username_unique_validation),
    path('phone-number-unique-validation/', views.phone_number_unique_validation),
    path('send-change-email-code/', views.send_change_email_code),
    path('check-change-email-code/', views.check_change_email_code_email),
    path('send-change-phone-number-code/', views.send_change_phone_code),
    path('check-change-phone-number-code/', views.check_change_phone_number_code_email),
    path('buy-tarif/<int:pk>/', views.buy_tarif),
    path('check-tarif-payment/<slug:id>/',views.check_tarif_payment),
    path('joined-user-statistic/',views.get_joined_user_statistic),
    path('get-popular-masters/',views.get_popular_masters),
    path('get-stripe-account/',views.get_stripe_account),
    path("activate-inactivate/",views.activate_inactvate_user),
]
