from django.contrib import admin
from .models import Category, General, Service, UserRole, Gender,Language

admin.site.register(Category)
admin.site.register(Service)
admin.site.register(UserRole)
admin.site.register(Gender)
admin.site.register(Language)
admin.site.register(General)
