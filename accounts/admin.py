from django.contrib import admin
from .models import Profile,BankAccount ,SocialLink, Product, Category, Subcategory, CustomerOrder, OrderItem, DeliveryAddress, Brand, Banner, Productimg, OrderProductImage
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    #fields = ("","")
    # inlines = [ ]
    list_display = ('id', 'user', 'phone', 'city', "country", "user_type", "company_name")
    # list_filter = ("status",)
    # list_editable = ()
    list_display_links = ("id", 'user', )
    list_per_page = 10
    search_fields = ("id", 'user__username',)



class BankAccountAdmin(admin.ModelAdmin):
    # inlines = [Inline_ProductImage, Inline_ProductAlternative]
    fields = ("vendor_profile","bank_name", "account_number",  "swift_code",
              "account_name", "country","paypal_email","description",)
    list_display = ("id", "vendor_profile", "bank_name","account_number",
                    "swift_code", "account_name","country","paypal_email",)
    list_display_links = ("id", "bank_name", "paypal_email")

    search_fields = ("account_name", )
    list_per_page = 10

class SocialLinkAdmin(admin.ModelAdmin):
    # inlines = [Inline_ProductImage, Inline_ProductAlternative]
    fields = ("vendor_profile","facebook", "twitter",  "instagram",
              "pinterest",)
    list_display = ("id", "vendor_profile", "facebook","twitter",
                    "instagram", "pinterest",)
    list_display_links = ("id", "vendor_profile", )
    

    search_fields = ("id", )
    list_per_page = 10    

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'offer_percent', 'actual_price', 'product_rating', 'stock')
    list_filter = ('category', 'price', 'product_rating')
    search_fields = ('name', 'description')
    ordering = ('-price',)
    readonly_fields = ('product_rating',)
    fieldsets = (
        (None, {
            'fields': ('vendor','name', 'category','subcategory', 'brand', 'price', 'offer_percent', 'actual_price', 'description', 'stock', 'stock_status', 'min_order_quantity', 'delivery_charge')
        }),
        ('Additional Information', {
            'classes': ('collapse',),
            'fields': ('product_rating', ),
        }),
    )

admin.site.register(Profile,ProfileAdmin)
admin.site.register(BankAccount,BankAccountAdmin)
admin.site.register(SocialLink,SocialLinkAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Productimg)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(CustomerOrder)
admin.site.register(OrderProductImage)
admin.site.register(OrderItem)
admin.site.register(DeliveryAddress)
admin.site.register(Brand)
admin.site.register(Banner)