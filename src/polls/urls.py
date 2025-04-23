from django.urls import path

from polls import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.product, name='product'),
    path('order/<int:order_id>/', views.order, name='order'),
]