import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Meep, Challenge, Cryptocurrency, Portfolio
from .forms import MeepForm, SignUpForm, ProfilePicForm, ChallengeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic

# Generate a new mnemonic
mnemonic = Mnemonic().generate()


def home(request):
    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request, ("Your Meep Has Been Posted!"))
                return redirect('home')

        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps": meeps, "form": form})
    else:
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps": meeps})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles": profiles})
    else:
        messages.success(
            request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def unfollow(request, pk):
    if request.user.is_authenticated:
        # Get the profile to unfollow
        profile = Profile.objects.get(user_id=pk)
        # Unfollow the user
        request.user.profile.follows.remove(profile)
        # Save our profile
        request.user.profile.save()

        # Return message
        messages.success(
            request, (f"You Have Successfully Unfollowed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        messages.success(
            request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def follow(request, pk):
    if request.user.is_authenticated:
        # Get the profile to unfollow
        profile = Profile.objects.get(user_id=pk)
        # Unfollow the user
        request.user.profile.follows.add(profile)
        # Save our profile
        request.user.profile.save()

        # Return message
        messages.success(
            request, (f"You Have Successfully Followed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        messages.success(
            request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

        # Post Form logic
        if request.method == "POST":
            # Get current user
            current_user_profile = request.user.profile
            # Get form data
            action = request.POST['follow']
            # Decide to follow or unfollow
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            # Save the profile
            current_user_profile.save()

        return render(request, "profile.html", {"profile": profile, "meeps": meeps})
    else:
        messages.success(
            request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'followers.html', {"profiles": profiles})
        else:
            messages.success(request, ("That's Not Your Profile Page..."))
            return redirect('home')
    else:
        messages.success(
            request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'follows.html', {"profiles": profiles})
        else:
            messages.success(request, ("That's Not Your Profile Page..."))
            return redirect('home')
    else:
        messages.success(
            request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(
                request, ("You Have Been Logged In!  Get MEEPING!"))
            return redirect('home')
        else:
            messages.success(
                request, ("There was an error logging in. Please Try Again..."))
            return redirect('login')

    else:
        return render(request, "login.html", {})


def logout_user(request):
    logout(request)
    messages.success(
        request, ("You Have Been Logged Out. Sorry to Meep You Go..."))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # Log in user
            user = authenticate(username=username, password=password)
            login(request, user)

            # Create a wallet from the mnemonic
            wallet = Wallet.create(f'{username}_wallet', witness_type='segwit',
                                   keys=mnemonic, network='testnet')
            # Get the first key in the wallet
            key = wallet.get_key()

            messages.success(
                request, (f'Public Address: {key.address}, Private Key:{key.wif}'))
            return redirect('home')

    return render(request, "register.html", {'form': form})


"""
def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
            # second_name = form.cleaned_data['second_name']
            # email = form.cleaned_data['email']
            # Log in user
            user = authenticate(username=username, password=password)
            login(request, user)
        

            messages.success(
                request, ("You have successfully registered! Welcome!"))
            return redirect('home')

    return render(request, "register.html", {'form': form})
"""


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        # Get Forms
        user_form = SignUpForm(request.POST or None,
                               request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(
            request.POST or None, request.FILES or None, instance=profile_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            login(request, current_user)
            messages.success(request, ("Your Profile Has Been Updated!"))
            return redirect('home')

        return render(request, "update_user.html", {'user_form': user_form, 'profile_form': profile_form})
    else:
        messages.success(
            request, ("You Must Be Logged In To View That Page..."))
        return redirect('home')


def meep_like(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if meep.likes.filter(id=request.user.id):
            meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)

        return redirect(request.META.get("HTTP_REFERER"))

    else:
        messages.success(
            request, ("You Must Be Logged In To View That Page..."))
        return redirect('home')


def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if meep:
        return render(request, "show_meep.html", {'meep': meep})
    else:
        messages.success(request, ("That Meep Does Not Exist..."))
        return redirect('home')


def delete_meep(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        # Check to see if you own the meep
        if request.user.username == meep.user.username:
            # Delete The Meep
            meep.delete()

            messages.success(request, ("The Meep Has Been Deleted!"))
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.success(request, ("You Don't Own That Meep!!"))
            return redirect('home')

    else:
        messages.success(request, ("Please Log In To Continue..."))
        return redirect(request.META.get("HTTP_REFERER"))


def edit_meep(request, pk):
    if request.user.is_authenticated:
        # Grab The Meep!
        meep = get_object_or_404(Meep, id=pk)

        # Check to see if you own the meep
        if request.user.username == meep.user.username:

            form = MeepForm(request.POST or None, instance=meep)
            if request.method == "POST":
                if form.is_valid():
                    meep = form.save(commit=False)
                    meep.user = request.user
                    meep.save()
                    messages.success(request, ("Your Meep Has Been Updated!"))
                    return redirect('home')
            else:
                return render(request, "edit_meep.html", {'form': form, 'meep': meep})

        else:
            messages.success(request, ("You Don't Own That Meep!!"))
            return redirect('home')

    else:
        messages.success(request, ("Please Log In To Continue..."))
        return redirect('home')


def search(request):
    if request.method == "POST":
        # Grab the form field input
        search = request.POST['search']
        # Search the database
        searched = Meep.objects.filter(body__contains=search)

        return render(request, 'search.html', {'search': search, 'searched': searched})
    else:
        return render(request, 'search.html', {})

###########################################################################


@login_required
def create_challenge(request):
    if request.user.is_authenticated:
        form = ChallengeForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                challenge = form.save(commit=False)
                challenge.sender = request.user
                # Set receiver_username
                challenge.receiver_username = form.cleaned_data['receiver_username']
                challenge.save()
                messages.success(request, "Your Challenge Has Been Created!")
                return redirect('home')
    else:
        form = None
    return render(request, 'home.html', {})


@login_required
def accept_challenge(request, challenge_id):
    challenge = Challenge.objects.get(id=challenge_id)
    if challenge.receiver_username == request.user.username:
        challenge.receiver = request.user
        challenge.status = 'accepted'
        challenge.save()
        return redirect('home')
    else:
        return redirect('home')  # Redirect to home or an error page


def reject_challenge(request, challenge_id):

    challenge = Challenge.objects.get(id=challenge_id)
    if challenge.receiver_username == request.user.username:

        challenge.status = 'rejected'
        challenge.save()
        return redirect('profile', username=request.user.username)
    else:
        return redirect('home')  # Redirect to home or an error page

# create a challange


def challenge_page(request):
    form = ChallengeForm()
    return render(request, 'create_challenge.html', {'form': form})


def user_challenges(request):
    if request.user.is_authenticated:
        user_challenges = Challenge.objects.filter(
            receiver_username=request.user.username)
        return render(request, 'user_challenges.html', {'challenges': user_challenges})
    else:
        # Handle case when user is not authenticated
        return render(request, 'user_challenges.html', {'challenges': None})

###########################################################################


@login_required(login_url="login")
def portfolio_view(request):
    # get the current logged in user
    current_user = request.user

    # get the list of cryptocurrencies owned by the current user
    user_cryptocurrencies = Cryptocurrency.objects.filter(user=current_user)

    if user_portfolio := Portfolio.objects.filter(user=current_user).first():
        portfolio = Portfolio.objects.get(user=current_user)

        # get all the crypto currencies in the portfolio and recalculate the total value of the portfolio
        new_portfolio_value = 0

        user_cryptocurrencies = Cryptocurrency.objects.filter(
            user=current_user)
        for cryptocurrency in user_cryptocurrencies:
            total_value = cryptocurrency.quantity * cryptocurrency.current_price
            new_portfolio_value += total_value

        portfolio.total_value = new_portfolio_value
        portfolio.save()

        context = {
            'current_user': current_user,
            'user_cryptocurrencies': user_cryptocurrencies,
            'user_portfolio': user_portfolio,
            'new_portfolio_value': new_portfolio_value,
        }
    else:
        context = {
            'current_user': current_user,
            'user_cryptocurrencies': user_cryptocurrencies,
            'user_portfolio': user_portfolio,


        }
    return render(request, 'portfolio.html', context)


def dash_view(request):
    # get the top 10 crypto currencies by market cap
    top_10_crypto_url_global = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=10&page=1&sparkline=true'
    top_10_crypto_data_global = requests.get(top_10_crypto_url_global).json()

    # check if user is logged in
    if request.user.is_authenticated:

        # get user's crypto currencies
        user_cryptocurrencies = Cryptocurrency.objects.filter(
            user=request.user)
        user_portfolio = Portfolio.objects.filter(user=request.user).first()

        # get the prices and price changes for user's cryptocurrencies
        names = [crypto.name for crypto in user_cryptocurrencies]
        symbols = [crypto.symbol for crypto in user_cryptocurrencies]
        ids = [crypto.id_from_api for crypto in user_cryptocurrencies]
        prices = []

        # NOTE: Only showing the price change for the last 24 hours for now and not the percentage change to reduce the number of api calls. Only 10-20 api calls per minute are allowed for free users. Otherwise, I could have used the /coins/{id}/market_chart?vs_currency=usd&days=1 endpoint to get the price change for the last 24 hours and calculate the percentage change from that.
        for crytpo_id in ids:
            prices_url = f'https://api.coingecko.com/api/v3/simple/price?ids={crytpo_id}&vs_currencies=usd&include_24hr_change=true'
            prices_data = requests.get(prices_url).json()

            price_change = prices_data[crytpo_id]['usd_24h_change']
            prices.append(price_change)

        # make a dictionary out of the names and prices
        crypto_price_changes = dict(zip(names, prices))

        context = {
            'top_10_crypto_data_global': top_10_crypto_data_global,
            'user_cryptocurrencies': user_cryptocurrencies,
            'user_portfolio': user_portfolio,
            'crypto_price_changes': crypto_price_changes,
        }

    else:
        context = {'top_10_crypto_data_global': top_10_crypto_data_global}
    return render(request, 'dash.html', context)


@login_required(login_url="login")
def search_view(request):
    if request.method != 'POST':
        # return HTTP status code 405 if the request method is not POST along with a message
        return HttpResponseNotAllowed(['POST'], 'Only POST requests are allowed for this view. Go back and search a cryptocurrency.')

    if not (search_query := request.POST.get('search_query')):
        return HttpResponse('No crypto currency found based on your search query.')

    api_url = f'https://api.coingecko.com/api/v3/search?query={search_query}'
    response = requests.get(api_url)
    search_results = response.json()
    try:
        data = search_results['coins'][0]
    except IndexError:
        return HttpResponse('No crypto currency found based on your search query.')
    coin_id = data['id']
    image = data['large']
    symbol = data['symbol']
    market_cap = data['market_cap_rank']

    # check if the crypto currency is already in the users portfolio and pass that information to the template
    current_user = request.user
    is_already_in_portfolio = False

    user_cryptocurrencies = Cryptocurrency.objects.filter(user=current_user)
    for cryptocurrency in user_cryptocurrencies:
        if cryptocurrency.name.lower() == coin_id.lower():
            is_already_in_portfolio = True

    context = {
        'data': data,
        'coin_id': coin_id,
        'image': image,
        'symbol': symbol,
        'market_cap': market_cap,
        'is_already_in_portfolio': is_already_in_portfolio,
    }
    return render(request, 'search_crypto.html', context)


@login_required(login_url="login")
def add_to_portfolio_view(request):
    if request.method != 'POST':
        return HttpResponse('Need a crypto currency to add to your portfolio. Go back to the home page and search for a crypto currency.')

    # get values from the form
    coin_id = request.POST.get('id')
    quantity = request.POST.get('quantity')
    print(coin_id)

    # get the crypto currency data from the coingecko api based on the coin id
    api_url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
    response = requests.get(api_url)
    data = response.json()
    print(data)
    # store the name, symbol, current price, and market cap rank of the crypto currency
    user = request.user
    name = data['name']
    id_from_api = data['id']
    symbol = data['symbol']
    current_price = data['market_data']['current_price']['usd']

    try:
        # save the crypto currency to the database
        crypto_currency = Cryptocurrency.objects.create(
            user=user,
            name=name,
            id_from_api=id_from_api,
            symbol=symbol,
            quantity=quantity,
            current_price=current_price,
        )
    except IntegrityError:
        crypto_currency = Cryptocurrency.objects.get(user=user, name=name)
        crypto_currency.quantity += int(quantity)

    crypto_currency.save()

    # calculate the total value of the crypto currency
    total_value = int(quantity) * int(current_price)

    # save the total value of the crypto currency to the database in the portfolio model
    # check if the user already has a portfolio
    if Portfolio.objects.filter(user=user).exists():
        portfolio = Portfolio.objects.get(user=user)
        portfolio.total_value += total_value
    else:
        portfolio = Portfolio(user=user, total_value=total_value)

    portfolio.save()
    messages.success(request, f'{name} has been added to your portfolio.')

    # if all the above steps are successful, redirect the user to the portfolio page
    return redirect('portfolio')


@login_required(login_url="login")
def delete_from_portfolio_view(request, pk):
    # get the current logged in user
    user = request.user

    # get the crypto currency object from the database
    crypto_currency = Cryptocurrency.objects.get(pk=pk)

    # delete the crypto currency from the database
    crypto_currency.delete()

    # update the total value of the portfolio
    portfolio = Portfolio.objects.get(user=user)

    # get all the crypto currencies in the portfolio and recalculate the total value of the portfolio
    user_cryptocurrencies = Cryptocurrency.objects.filter(user=user)
    for cryptocurrency in user_cryptocurrencies:
        total_value = cryptocurrency.quantity * cryptocurrency.current_price
        portfolio.total_value += total_value

    portfolio.save()

    # send an alert to the user that the crypto currency has been deleted from the portfolio
    messages.warning(
        request, f'{crypto_currency.name} has been deleted from your portfolio.')

    return redirect('portfolio')
