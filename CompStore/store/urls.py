from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:category_slug>/', views.catalog, name='catalog_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('prebuilts/', views.prebuilts, name='prebuilts'),
    path('prebuilts/<slug:slug>/', views.prebuilt_detail, name='prebuilt_detail'),
    path('builder/', views.builder, name='builder'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.my_orders, name='my_orders'),
    path('search/', views.search, name='search'),
]
