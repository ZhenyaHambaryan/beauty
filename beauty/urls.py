from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('utils/', include('utils.urls')),
    path('files/', include('files.urls')),
    path('userdetails/', include('userdetails.urls')),
    path('timeline/', include('timeline.urls')),
    path('schedule/', include('schedule.urls')),
    path('notification/', include('notifications.urls')),
    path('statistic/', include('statistic.urls')),
    path('chat/', include('chat.urls')),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
 + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
