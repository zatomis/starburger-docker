import requests
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from geopy import distance

from coordinates.models import Location
from foodcartapp.models import (OrderState, Product, Restaurant,
                                RestaurantMenuItem, UserOrder)


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_location(address):
    location, created = Location.objects.get_or_create(
        address=address, defaults={"last_check": timezone.now()}
    )
    if created:
        coords = fetch_coordinates(settings.YANDEX_API_KEY, location.address)
        if coords:
            location.lon, location.lat = coords
            location.save()
    return location


def calculate_distance(location1, location2):
    coordinates_1 = location1.lat, location1.lon
    coordinates_2 = location2.lat, location2.lon
    if None not in coordinates_1 and None not in coordinates_2:
        return str(round(distance.distance(coordinates_1, coordinates_2).km, 2))
    else:
        return "Ошибка определения координат"


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    users = OrderState.objects.get_unique_user_id()
    user_products_in_restaurant = dict()

    for user in users:
        products = OrderState.objects.filter(order_id=user)
        product_in_restaurants = set()
        for product in products:
            restaurants = RestaurantMenuItem.objects.filter(product_id=product.product_id, availability=True)
            products_in_restaurants = [product_in_restaurants.add(restaurant.restaurant) for restaurant in restaurants]
            user_products_in_restaurant[user] = products_in_restaurants

    orders = UserOrder.objects.prefetch_related("order_states").total_price().\
        total_count().order_by('status').filter(status__gte=0)
    serialized_orders = [{
        "id": order.id,
        "status": order.get_status_display(),
        "firstname": order.firstname,
        "lastname": order.lastname,
        "phonenumber": order.phonenumber,
        "payment": order.get_payment_display(),
        "address": order.address,
        "available_restaurants": [{
            "restaurant": restaurant,
            "distance": calculate_distance(get_location(restaurant.address), get_location(order.address))
        } for restaurant in order.available_restaurants.all()],
        "comment": order.comment,
        "total_price": order.total_price,
        "total_count_position": order.total_count_position,
        "link": reverse("admin:foodcartapp_userorder_change", args=(order.id,)),
        "link_del": reverse("admin:foodcartapp_userorder_delete", args=(order.id,))
    } for order in orders]
    return render(request, template_name='order_items.html', context={"order_items": serialized_orders})
