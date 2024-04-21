from django.contrib import admin
from .models import Listing, Category, User, Comment, Bid
from django.contrib.auth.admin import UserAdmin

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "bid", "image", "creator")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "comment", "comment_datetime")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "user", "item")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
