from django.contrib import admin
from .models import Product,Customer,Cart,Payment,OrderPlaced,Wishlist
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import Group


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_title', 'discount_price', 'category', 'product_image']
    search_fields = ['title', 'category', 'id']
    list_filter = ['category']
    list_per_page = 10

    # Điều chỉnh fieldsets theo các trường có trong model Product của bạn
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['title', 'description', 'product_image']
        }),
        ('Giá', {
            'fields': ['selling_price', 'discount_price']
        }),
        ('Phân loại', {
            'fields': ['category']  
        })
    ]

    def product_title(self, obj):
        link = reverse("admin:app_product_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', link, obj.title)
    product_title.short_description = 'Title'

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'locality', 'city','zipcode','state']
@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'products', 'quantity']
    def products(self,obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link,obj.product.title)


@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'order_id', 'vnpay_order_id', 
                    'vnpay_payment_status', 'vnpay_payment_id', 'paid', 'created_at']
    list_filter = ['vnpay_payment_status', 'created_at']
    search_fields = ['order_id', 'vnpay_order_id', 'user__username']
    readonly_fields = ['paid']

    def paid(self, obj):
        return obj.paid
    paid.boolean = True  # Hiển thị dưới dạng icon boolean trong admin

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customers', 'products','quantity','ordered_date','status','payments']
    def customers(self,obj):
        link = reverse("admin:app_customer_change", args=[obj.customer.pk])
        return format_html('<a href="{}">{}</a>',link,obj.customer.name)
    def products(self,obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link,obj.product.  title)
    def payments(self,obj):
        link = reverse("admin:app_payment_change", args=[obj.payment.pk])
        return format_html('<a href="{}">{}</a>',link,obj.payment.vnpay_payment_id)

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'products']
    def products(self,obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link,obj.product.title)
    
admin.site.unregister(Group)