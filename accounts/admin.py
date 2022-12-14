from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
from django.utils.html import format_html

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "username", "last_login", "date_joined", "is_active")
    list_display_links = ("email", "first_name", "last_name") 
    readonly_fields = ("last_login", "date_joined")
    ordering = ('-date_joined', )

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def get_username(self, object):
        return object.user.username
    get_username.short_description = 'User'

    def thumbnail(self, object):
        if object.profile_picture:
            return format_html('<img src="{}" width=20 height=20 style="border-radius: 50%"></img>'.format(object.profile_picture.url))
    thumbnail.short_description = "Profile Picture"

    list_display = ["thumbnail", "get_username", "city", "state", "country"]

admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)