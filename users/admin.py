from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# This makes our custom user show up in the admin panel
admin.site.register(CustomUser, UserAdmin)