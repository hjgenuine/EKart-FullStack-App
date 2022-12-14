from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id, _check_equal

from orders.models import Order, OrderProduct

import requests

# Create your views here.
def register(request):
    form = RegistrationForm()

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            username = email.split("@")[0]
            
            user = Account.objects.create_user(first_name, last_name, username, email, password)
            user.phone_number = phone_number
            user.save()

            mail_subject = "Please activate your account"
            current_site = get_current_site(request)
            context = {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            }
            message = render_to_string("accounts/account_verification_email.html", context)
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()

            return redirect("/accounts/login?command=verification")
        else:
            form = RegistrationForm(request.POST)

    data = {"form": form}
    return render(request, "accounts/register.html", context=data)

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = auth.authenticate(email=email, password=password)
        if user:
            current_cart_id = _cart_id(request)
            if Cart.objects.filter(cart_id=current_cart_id).exists():
                current_cart = Cart.objects.get(cart_id=current_cart_id)
                items = CartItem.objects.filter(cart=current_cart)
            else:
                items = []

            auth.login(request, user)

            try:
                user_cart = Cart.objects.get(user=user)
                user_cart.cart_id = _cart_id(request)
            except:
                user_cart = Cart.objects.create(user=user, cart_id=_cart_id(request))

            user_items = CartItem.objects.filter(cart=user_cart)
            for item1 in items:
                itemAdded = False
                for item2 in user_items:
                    if item1.product == item2.product:
                        if _check_equal(item1.variations.all(), item2.variations.all()):
                            item2.quantity += item1.quantity
                            item2.save()
                            itemAdded = True
                            break
                if not itemAdded:
                    item1.cart = user_cart
                    item1.save()
            user_cart.save()

            try:
                url = request.META.get("HTTP_REFERER")
                queryString = requests.utils.urlparse(url).query
                queryDict = dict(x.split("=") for x in queryString.split("&"))
                if "next" in queryDict:
                    return redirect(queryDict["next"])
            except:
                return redirect("account:dashboard")
        else:
            messages.error(request, "Invalid Login Credentials.")

    return render(request, "accounts/login.html")

@login_required(login_url = "account:login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('account:login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations, your account has been successfully created.")
        return redirect("account:login")
    
    else:
        messages.error(request, "Invalid activation link.")
        return redirect("account:register")

@login_required(login_url = "account:login")
def dashboard(request):
    profile_pic = ""

    user_profile = UserProfile.objects.filter(user=request.user)
    if user_profile:
        user_profile = user_profile[0]
        if user_profile.profile_picture:
            profile_pic = user_profile.profile_picture.url

    order_cnt = Order.objects.filter(user=request.user, is_ordered=True).count()

    context = {"order_cnt": order_cnt, "profile_pic": profile_pic}

    return render(request, "accounts/dashboard.html", context)

@login_required(login_url = "account:login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by("-created_at")

    context = {"orders": orders}

    return render(request, "accounts/my_orders.html", context)

login_required(login_url = "account:login")
def edit_profile(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Your profile has been updated.")
            return redirect("account:edit_profile")

    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    if user_profile.profile_picture:
        context["profile_pic"] = user_profile.profile_picture.url
        
    return render(request, "accounts/edit_profile.html", context)

login_required(login_url = "account:login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = auth.authenticate(email=request.user.email, password=current_password)
        if user:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, "Password changed successfully.")
                return redirect("account:login")
            else:
                messages.error(request, "The passwords don't match.")
        else:
            messages.error(request, "The password you entered is incorrect.")

    return render(request, "accounts/change_password.html")

login_required(login_url = "account:login")
def order_details(request, order_id):
    order = Order.objects.filter(order_number=order_id, user=request.user)
    context = {}

    if order:
        order = order[0]

        first_name = order.first_name
        last_name = order.last_name
        address_line_1 = order.address_line_1
        address_line_2 = order.address_line_2
        city = order.city
        state = order.state
        country = order.country

        ordered_products = OrderProduct.objects.filter(order=order, user=request.user)
        subtotal, tax = 0, 0
        for product in ordered_products:
            subtotal += product.product_price * product.quantity
        tax = 0.18 * subtotal

        payment = order.payment
        status = payment.status
        grand_total = payment.amount_paid

        context = {"first_name": first_name, "last_name": last_name, "address_line_1": address_line_1, "address_line_2": address_line_2, "city": city, "state": state, "country": country, "order_date": order.updated_at, "order_number": order_id, "payment_id": payment.payment_id, "status": status, "products": ordered_products, "subtotal": subtotal, "tax": tax, "grand_total": grand_total}

    return render(request, "accounts/order_details.html", context)

def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email__exact=email).exists():
            user = Account.objects.get(email__exact=email)

            mail_subject = "Password Reset"
            current_site = get_current_site(request)
            context = {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            }
            message = render_to_string("accounts/reset_password_validate.html", context)
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()

            messages.success(request, "Password reset email has been sent.")

            return redirect("account:login")
        else:
            messages.error(request, "Account doesn't exist.")

    return render(request, "accounts/forgot_password.html")

def resetPasswordValidate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Reset your Password.")
        return redirect("account:resetPassword")
    else:
        messages.error(request, "Link has been Expired.")
        return redirect("account:login")

def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirmPassword = request.POST["confirmPassword"]
        if password != confirmPassword:
            messages.error(request, "Password doesn't match.")
        else:
            user = Account.objects.get(id=request.session.get("uid"))
            user.set_password(password)
            user.save()
            messages.success(request, "Password changed succesfully.")
            return redirect("account:login")
    return render(request, "accounts/reset_password.html")