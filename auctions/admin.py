from django.contrib import admin
from .models import Listing, Category, User

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "bid", "image", "creator")

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")

admin.site.register(Listing, ListingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)
