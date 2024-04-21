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
from .models import Bid


def index(request):
    listings = Listing.objects.all()
    user = request.user
    return render(request, "auctions/index.html", {
        "listings": listings,
        "user": user
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
    # create a new listing
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
            # check if the user specified a category
            if category:
                listing.category = category
                # check if the user gave a URL for the image
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
    user = request.user # get the authenticated user
    # check if the user is authenticated
    if user.is_authenticated:
        # check if the listing is in the user's watchlist
        is_in_watchlist = listing in user.watchlist.all()
    else:
        is_in_watchlist = False
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "is_in_watchlist": is_in_watchlist,
        "user": user
    })


@login_required(login_url="login")
def add_to_watchlist(request, listing_id):
    user = request.user # get the authenticated user
    if request.method == "POST":
        # get the listing
        listing = Listing.objects.get(pk=listing_id)
        # add the listing in the authenticated user's watchlist
        user.watchlist.add(listing)
        # redirect to the listing page
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    
    
@login_required(login_url="login")
def remove_to_watchlist(request, listing_id):
    user = request.user # get the authenticated user
    if request.method == "POST":
        # get the listing
        listing = Listing.objects.get(pk=listing_id)
        # remove the listing in the authenticated user's watchlist
        user.watchlist.remove(listing)
        # redirect to the listing page
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    

@login_required(login_url="login")
def user_watchlist(request):
    # this view render the wathclist template with all the authenticated user's listings
    user = request.user
    watchlists = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlists,
        "user": user
    })

@login_required(login_url="login")
def user_listings(request):
    user = request.user
    user_listings = Listing.objects.filter(creator=user)
    return render(request, "auctions/user_listings.html", {
        "user_listings": user_listings
    })
    

@login_required(login_url="login")
def bid(request, listing_id):
    message = "" # initialize the variable message with a empty string
    was_auctioned = False # intialize the variable to False
    user = request.user # get the authenticated user
    if request.method == "POST": # if the form is submited
        # get the listing by his id
        listing = Listing.objects.get(pk=listing_id)
        # retrieve the entered amount by converting it to a decimal number
        placed_bid = float(request.POST["bid"])
        # whene there is no bid and the user entered an amount lower than the starting price
        if listing.bid and placed_bid <= listing.bid:
            # render the template with an error message
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Error: Your bid must be higher than the current bid."
            })
        # whene there at list one bid and the user entered an amount lower than the current bid
        elif placed_bid <= listing.price:
            # render the template with an error message
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Error: Your bid must be higher than the starting price."
            })
        else:
            # if the bid is higher than the starting price and the current bid
            listing.bid = placed_bid
            # was_auctionned is now true
            was_auctioned = True
        # if was_auctionned is true (the bid meete the criteria)
        if was_auctioned:
            listing.save()  # save the modifictions
            # create a new bid object
            bid = Bid.objects.create(amount=placed_bid, user=user, item=listing)
            # render the template with a success message
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Your bid has been added successfully. You're in first position.",
            })
        # redirect to the same page
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "user": user,
        "bid": bid
        })


@login_required(login_url="login")
def close_auction(request, listing_id):
    user = request.user # get the authenticated user
    if request.method == "POST":
        # retrieve the listing with his id
        listing = Listing.objects.get(pk=listing_id)
        # mark the listing as inactive
        listing.is_active =  False
        # cheking if there is a list one bid
        if listing.bids.exists():
            # get the current bid
            highest_bid = listing.bids.order_by('-amount').first()
            # the winner is the authenticated user
            listing.winner = highest_bid.user
        else:
            # if there is no bid, there is no winner
            listing.winner = None
        listing.save() # save the chages
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "user": user,
    })

