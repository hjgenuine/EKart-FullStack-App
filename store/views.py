from django.shortcuts import get_object_or_404, render, redirect
from .models import Product, ProductGallery, ReviewRating
from category.models import Category
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

# Create your views here.
def store(request, category_slug=None):

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category, is_available=True).order_by("id")
        count = products.count()

        paginator = Paginator(products, 1)
        page = request.GET.get("page")
        products = paginator.get_page(page)
    else:
        products = Product.objects.all().filter(is_available=True).order_by("id")
        count = products.count()

        paginator = Paginator(products, 6)
        page = request.GET.get("page")
        products = paginator.get_page(page)

    data = {"products": products, "count": count}

    return render(request, "store/store.html", context=data)

def product_detail(request, category_slug=None, product_slug=None):
    data = {"purchased": False}

    if product_slug and category_slug:
        product =  get_object_or_404(Product, slug=product_slug, category__slug=category_slug)
        data["photos"] = ProductGallery.objects.filter(product=product)
        data["product"] = product
        data["reviews"] = ReviewRating.objects.filter(product=product, status=True).order_by("-created_at")

        purchased = False
        if request.user.is_authenticated:
            purchasedProducts = OrderProduct.objects.filter(user=request.user, product=product)

            for product in purchasedProducts:
                if product.payment.status == "COMPLETED":
                    purchased = True
                    break
        data["purchased"] = purchased

    return render(request, "store/product_detail.html", context=data)

def search(request):
    query = request.GET.get("keyword")

    if query:
        products = Product.objects.filter(Q(product_name__icontains=query) | Q(description__icontains=query))
        count = products.count()
    else:
        products = []
        count = 0

    data = {"products": products, "count": count}

    return render(request, "store/store.html", context=data)

@login_required(login_url = "account:login")
def submit_review(request, product_id):
    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            product = Product.objects.get(id=product_id)
            rating = form.cleaned_data["rating"]
            subject = form.cleaned_data["subject"]
            review = form.cleaned_data["review"]
            ip = request.META.get('REMOTE_ADDR')

            try:
                review_object = ReviewRating.objects.get(user=request.user, product=product)
            except:
                review_object = ReviewRating()
                review_object.user = request.user
                review_object.product = product

            review_object.rating = rating
            review_object.subject = subject
            review_object.review = review
            review_object.ip = ip
            review_object.save()

            messages.success(request, "Thanks for your review.")
        
        else:
            messages.error(request, "Oops. You might have missed something.")

    return redirect(request.META.get('HTTP_REFERER'))
