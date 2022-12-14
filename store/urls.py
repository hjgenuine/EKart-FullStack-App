from django.urls import path
from . import views

app_name = "store"
urlpatterns = [
    path('', views.store, name="store"),
    path('category/<slug:category_slug>/', views.store, name="categorical_view"),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name="product_view"),
    path('search/', views.search, name="search"),
    path('submit_review/<int:product_id>/', views.submit_review, name="submit_review"),
] 
