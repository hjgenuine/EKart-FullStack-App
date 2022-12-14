from django.contrib import admin
from . import models

class OrderProductInline(admin.TabularInline):
    model = models.OrderProduct
    readonly_fields = ("payment", "user", "product", "product_price", "quantity", "is_ordered")
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "first_name", "last_name", "phone", "email", "city", "order_total", "tax", "status", "is_ordered"]
    list_filter = ["status", "is_ordered"]
    search_fields = ["order_number", "first_name", "last_name", "phone", "email"]
    inlines = [OrderProductInline, ]
    list_per_page = 20

class PaymentsAdmin(admin.ModelAdmin):
    list_display = ["user", "payment_id", "payment_method", "amount_paid", "status"]
    list_filter = ["status"]
    search_fields = ["payment_id", "user__email"]
    list_per_page = 20

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ["order", "payment", "user", "product", "quantity", "product_price", "is_ordered"]
    list_filter = ["payment", "is_ordered", "user__email"]
    search_fields = ["order__order_number", "user__email"]
    list_per_page = 20

# Register your models here.
admin.site.register(models.Payment, PaymentsAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderProduct, OrderProductAdmin)