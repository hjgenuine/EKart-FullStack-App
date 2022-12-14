from typing import Counter
from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem
from store.models import Product, Variation

def _check_equal(q1, q2):
    return Counter(q1) == Counter(q2)

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []

    if request.method == "POST":
        for key in request.POST:
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variation)
            except:
                pass


    product = Product.objects.get(id=product_id) 

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )

    cart.save()
    
    cartItem = None
    itemExists = CartItem.objects.filter(product=product, cart=cart).exists()
    if itemExists:
        cartItems = CartItem.objects.filter(product=product, cart=cart)

        for item in cartItems:
            q1, q2 = list(item.variations.all()), product_variations
            if _check_equal(q1, q2):
                cartItem = item
        
        if cartItem:
            cartItem.quantity += 1
        
    if not cartItem:
        cartItem = CartItem.objects.create(product=product, cart=cart, quantity=1)

        if len(product_variations) > 0:
            cartItem.variations.clear()
            for item in product_variations:
                cartItem.variations.add(item)
    
    cartItem.save()
    
    return redirect('cart:cart')

def remove_cart(request, product_id, cartItem_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cartItem = CartItem.objects.get(product=product, cart=cart, id=cartItem_id)

        if cartItem.quantity > 1:
            cartItem.quantity -= 1
            cartItem.save()
        else:
            cartItem.delete()

    except:
        pass

    return redirect('cart:cart')

def remove_cart_item(request, product_id, cartItem_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cartItem = CartItem.objects.get(product=product, cart=cart, id=cartItem_id)

        cartItem.delete()
    except:
        pass

    return redirect('cart:cart')

def cart(request):
    items, price, tax, grand_price, quantity = [], 0, 0, 0, 0
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in items:
            price += item.product.price * item.quantity
            quantity += item.quantity
        tax = (18 * price) / 100
        grand_price = price + tax
    except Cart.DoesNotExist:
        pass
    
    grand_price = "{:,}".format(grand_price)
    price = "{:,}".format(price)
    
    data = {"items": items, "price": price, "tax": tax, "grand_price": grand_price, "quantity": quantity}

    return render(request, "store/cart.html", context=data)

@login_required(login_url="account:login")
def checkout(request):
    items, price, tax, grand_price, quantity = [], 0, 0, 0, 0
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in items:
            price += item.product.price * item.quantity
            quantity += item.quantity
        tax = (18 * price) / 100
        grand_price = price + tax
    except Cart.DoesNotExist:
        pass
    
    grand_price = "{:,}".format(grand_price)
    price = "{:,}".format(price)
    
    data = {"items": items, "price": price, "tax": tax, "grand_price": grand_price, "quantity": quantity}

    return render(request, "store/checkout.html", data)