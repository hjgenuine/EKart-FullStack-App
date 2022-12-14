import json
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import JsonResponse

from carts.models import Cart
from carts.views import _cart_id
from carts.models import CartItem

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .forms import OrderForm
from .models import Order, OrderProduct, Payment

import datetime

from carts.views import _check_equal

import time

# Create your views here.
@login_required(login_url="account:login")
def place_order(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cartItems = CartItem.objects.filter(cart=cart)
    if cartItems.exists(): 
        price, grand_price, tax, quantity = 0, 0, 0, 0
        for item in cartItems:
            price += item.product.price * item.quantity
            quantity += item.quantity
        tax = (18 * price) / 100
        grand_price = price + tax

        if request.method == "POST":
            form = OrderForm(request.POST)
            if form.is_valid():
                order = Order()
                order.user = request.user
                order.first_name = form.cleaned_data["first_name"]
                order.last_name = form.cleaned_data["last_name"]
                order.phone = form.cleaned_data["phone"]
                order.email = form.cleaned_data["email"]
                order.address_line_1 = form.cleaned_data["address_line_1"]
                order.address_line_2 = form.cleaned_data["address_line_2"]
                order.country = form.cleaned_data["country"]
                order.state = form.cleaned_data["state"]
                order.city = form.cleaned_data["city"]
                order.order_note = form.cleaned_data["order_note"]
                order.order_total = grand_price
                order.tax = tax
                order.ip = request.META.get('REMOTE_ADDR')
                order.save()

                yr = datetime.date.today().year
                dt = datetime.date.today().day
                mt = datetime.date.today().month
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(order.id)
                order.order_number = order_number
                order.save()

                orderedProducts = []
                for item in cartItems:
                    orderedProduct = OrderProduct(
                        order = order,
                        user = request.user,
                        product = item.product,
                        quantity = item.quantity,
                        product_price = item.sub_total()
                    )
                    orderedProduct.save()
                    for variation in item.variations.all():
                        orderedProduct.variations.add(variation)
                    orderedProduct.save()
                    orderedProducts.append(orderedProduct)

                context = {
                    "order": Order.objects.get(user=request.user, order_number=order_number, is_ordered=False),
                    "cart_items": orderedProducts,
                    "price": price, 
                    "grand_price": grand_price, 
                    "tax": tax, 
                    "quantity": quantity,
                }
                return render(request, "orders/payments.html", context)

    return redirect("store:store")

@login_required(login_url="account:login")
def payments(request):
    body = json.loads(request.body)
    
    order = Order.objects.get(user=request.user, order_number=body["orderID"], is_ordered=False)

    payment = Payment(
        user = request.user,
        payment_id = body["transID"],
        payment_method = body["paymentMethod"],
        amount_paid = order.order_total,
        status = body["status"]
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    orderedProducts = OrderProduct.objects.filter(order=order, user=request.user, is_ordered=False)
    for orderedProduct in orderedProducts:
        orderedProduct.payment = payment
        orderedProduct.is_ordered = True
        orderedProduct.save()

    cart = Cart.objects.get(cart_id=_cart_id(request))
    for orderedProduct in orderedProducts:
        product = orderedProduct.product
        cartItems = CartItem.objects.filter(cart=cart, product=product)
        for item in cartItems:
            if _check_equal(item.variations.all(), orderedProduct.variations.all()):
                item.quantity -= orderedProduct.quantity
                item.save()
                if item.quantity <= 0: item.delete()
                break
        product.stock -= orderedProduct.quantity
        product.save()

    mail_subject = "Order Confirmation"
    context = {
        "user": order.user,
        "order": order,
    }
    message = render_to_string("orders/order_confirmation_email.html", context)
    to_email = order.email
    send_email = EmailMessage(mail_subject, message, to=[to_email,])
    send_email.send()

    data = {
        "order_number": order.order_number,
        "payment_id": body["transID"],
    }
    return JsonResponse(data)

def order_complete(request):
    order_number = request.GET.get("order_number")
    payment_id = request.GET.get("payment_id")
    
    order = Order.objects.get(order_number=order_number, user=request.user)
    first_name = order.first_name
    last_name = order.last_name
    address_line_1 = order.address_line_1
    address_line_2 = order.address_line_2
    city = order.city
    state = order.state
    country = order.country
    
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    order_date = dt_string.replace(" ", ", ")

    ordered_products = OrderProduct.objects.filter(order=order, user=request.user)
    subtotal, tax = 0, 0
    for product in ordered_products:
        subtotal += product.product_price * product.quantity
    tax = 0.18 * subtotal

    payment = Payment.objects.get(payment_id=payment_id, user=request.user)
    status = payment.status
    grand_total = payment.amount_paid

    context = {"first_name": first_name, "last_name": last_name, "address_line_1": address_line_1, "address_line_2": address_line_2, "city": city, "state": state, "country": country, "order_date": order_date, "order_number": order_number, "payment_id": payment_id, "status": status, "products": ordered_products, "subtotal": subtotal, "tax": tax, "grand_total": grand_total}
    return render(request, "orders/order_complete.html", context)