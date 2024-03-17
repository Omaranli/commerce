from django.contrib import admin

# Register your models here.
from .models import Listing, Category

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "bid", "image", "creator")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")

admin.site.register(Listing)
admin.site.register(Category)