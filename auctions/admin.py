from django.contrib import admin
from .models import Listing, Category, User  # Import User model if you have defined one
from django.contrib.auth.admin import UserAdmin

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "bid", "image", "creator")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")

admin.site.register(Listing, ListingAdmin)
admin.site.register(Category, CategoryAdmin)

# Use UserAdmin for the User model if you have defined a custom User model
admin.site.register(User, UserAdmin)
