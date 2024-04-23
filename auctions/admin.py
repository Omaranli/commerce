from django.contrib import admin
from .models import Listing, Category, User, Comment, Bid
from django.contrib.auth.admin import UserAdmin


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)

admin.site.register(Listing)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Comment)
admin.site.register(Bid)
