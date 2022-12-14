from django.contrib import admin
from . import models
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail("image")
class ProductGalleryInline(admin.TabularInline):
    model = models.ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('product_name',)}
    list_display = ("product_name", "price", "stock", "category", "modified_date", "is_available")
    inlines = [ProductGalleryInline,]

class VariationAdmin(admin.ModelAdmin):
    list_display = ("product", "variation_category", "variation_value", "is_active")
    list_editable = ("is_active",)
    list_filter = ("product", "variation_category")

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating")
    list_filter = ("product",)

admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Variation, VariationAdmin)
admin.site.register(models.ReviewRating, ReviewRatingAdmin)
admin.site.register(models.ProductGallery)