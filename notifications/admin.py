from notifications.models import EmailTypes, Notification, NotificationType
from django.contrib import admin

admin.site.register(EmailTypes)
admin.site.register(NotificationType)
admin.site.register(Notification)
