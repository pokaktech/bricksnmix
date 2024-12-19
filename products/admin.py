from django.contrib import admin
from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'name', 'category', 'price', 'offer_percent', 'brand', 'actual_price', 'stock')
    list_filter = ('category', 'price', 'brand', 'vendor')
    search_fields = ('name', 'description')
    ordering = ('-price',)
    # readonly_fields = ('product_rating',)
    fieldsets = (
        (None, {
            'fields': ('vendor','name', 'category','subcategory', 'brand', 'price', 'offer_percent', 'actual_price', 'description', 'stock', 'stock_status', 'min_order_quantity', 'min_order_quantity_two', 'min_order_quantity_three', 'min_order_quantity_four', 'min_order_quantity_five', 'delivery_charge')
        }),
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Productimg)
admin.site.register(Brand)
# admin.site.register(Banner)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(RatingReview)
admin.site.register(Banner)
admin.site.register(BannerProduct)