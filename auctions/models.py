from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Category(models.Model):
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category_name}"

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watched_by")

class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    publication_datetime = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="wins")

    def __str__(self):
        return f"\"{self.title}\""



class Bid(models.Model):
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")


    def __str__(self):
        return f"${self.amount} bid by {self.user} for {self.item}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    comment_datetime = models.DateTimeField(default=timezone.now)
    

    def __str__(self):
        return f"{self.comment_datetime}: {self.listing} comment by {self.user}"