from django.contrib import admin
from django.shortcuts import redirect, reverse
from django.templatetags.static import static
from django.utils.encoding import iri_to_uri
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import (OrderState, Product, ProductCategory, Restaurant,
                     RestaurantMenuItem, UserOrder)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline,
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = (RestaurantMenuItemInline, )

    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass

class OrderMenuItemInline(admin.TabularInline):
    model = OrderState
    extra = 0

@admin.register(UserOrder)
class UserOrderAdmin(admin.ModelAdmin):
    list_display_links = [
        'phonenumber',
    ]
    list_display = [
        'firstname',
        'lastname',
        'address',
        'phonenumber',
        'status',
        'registr_date',
        'call_date',
        'delivered_date',
    ]
    inlines = [
        OrderMenuItemInline
    ]

    def response_change(self, request, obj):
        res = super(UserOrderAdmin, self).response_change(request, obj)
        if "next" in request.GET and url_has_allowed_host_and_scheme(request.GET["next"], None):
            url = iri_to_uri(request.GET["next"])
            return redirect(url)
        else:
            return res


@admin.register(RestaurantMenuItem)
class AdminRestaurantMenuItem(admin.ModelAdmin):
    list_display = [
        'restaurant',
        'product',
        'availability',
    ]



@admin.register(OrderState)
class AdminOrderState(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'product',
        'quantity',
        'price',
    ]

    ordering = ('-order',)

    def response_change(self, request, obj):
        res = super(AdminOrderState, self).response_change(request, obj)
        if "next" in request.GET and url_has_allowed_host_and_scheme(request.GET["next"], None):
            url = iri_to_uri(request.GET["next"])
            return redirect(url)
        else:
            return res

    def save_formset(self, request, obj, form, change):
        if not obj.pk or 'quantity' in form.changed_data:
            item_price = obj.item.price if obj.item else 0
            obj.price = item_price * obj.quantity
        super().save_model(request, obj, form, change)

    # def save_formset(self, request, form, formset, change):
    #     instances = formset.save(commit=False)
    #     for instance in instances:
    #         product_price = instance.product.price
    #         instance.price = product_price
    #         instance.save()
    #     formset.save_m2m()
