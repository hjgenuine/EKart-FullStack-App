from django.urls import path
from . import views

app_name = "account"
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("resetPasswordValidate/<uidb64>/<token>/", views.resetPasswordValidate, name="resetPasswordValidate"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("change_password/", views.change_password, name="change_password"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("order_details/<int:order_id>", views.order_details, name="order_details"),
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    path("resetPassword/", views.resetPassword, name="resetPassword"),
    path("", views.dashboard, name="accounts"),
]