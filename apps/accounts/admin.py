from django.contrib import admin
from apps.accounts.models import User, UserRole, StaffProfile,CustomerProfile


# Register your models here.
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in UserRole._meta.fields)
    search_fields = ['name']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in User._meta.fields)
    search_fields = ['name']

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in StaffProfile._meta.fields)
    search_fields = ['name']

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in CustomerProfile._meta.fields)
    search_fields = ['name']
