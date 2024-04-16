from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User
from .models import Listing
from .models import Category
from .models import Comment


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
    })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# create listing :form
class ListingForm(forms.Form):
    title = forms.CharField(
        max_length=100, 
        label='title',
        widget=forms.TextInput(attrs={
            'placeholder': '*enter the title',
            'class': 'col-12 input',
            'name': 'title'
        })
        
    )
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'col-12 input',
            'name': 'category'
    }))

    price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'col-12 input',
            'placeholder': '*starting bid',
            'name': 'price',
            'min': 1
        })
        )
    image = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'col-12 input',
            'placeholder': 'enter the image\'s url',
            'name': 'image'
        })
    )
    description = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'placeholder': '*description',
            'name': 'description',
            'class': 'col-12 textarea',
            'id': 'exampleFormControlTextarea1',
            'rows': "5"
        })
        )


@login_required(login_url="login")
def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data['title']
            category = form.cleaned_data.get('category')
            price = form.cleaned_data['price']
            image = form.cleaned_data.get('image') 
            description = form.cleaned_data['description']
            listing = Listing.objects.create(title=title, price=price, description=description, creator=user)
            if category:
                listing.category = category
            if image:
                listing.image = image
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()
    return render(request, "auctions/new_listing.html", {
        "form": form
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    is_in_watchlist = listing in user.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "is_in_watchlist": is_in_watchlist
    })


@login_required(login_url="login")
def add_to_watchlist(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        user.watchlist.add(listing) 
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    
    
@login_required(login_url="login")
def remove_to_watchlist(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        user.watchlist.remove(listing) 
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    

@login_required(login_url="login")
def watchlist(request):
    user = request.user
    watchlists = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlists
    })