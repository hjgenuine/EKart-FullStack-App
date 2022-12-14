from unicodedata import category
from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account
from django.db.models import Avg

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)

    def get_rating(self):
        ratings = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg("rating"))
        if ratings["average"]:
            return float("%.2f" % (ratings["average"] / len(ratings)))
        return 0

    def rating_cnt(self):
        ratings = ReviewRating.objects.filter(product=self, status=True)
        return len(ratings)

    def get_url(self):
        return reverse("store:product_view", kwargs={"category_slug": self.category.slug, "product_slug": self.slug})

    def __str__(self):
        return self.product_name

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category="color", is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category="size", is_active=True)

variation_category_choices = (
    ("size", "size"),
    ("color", "color"),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.TimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.subject

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store/products/")

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = "product gallery"
        verbose_name_plural = "product gallery"

