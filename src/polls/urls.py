from django.urls import path

from polls import views

app_name = 'polls'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.product, name='product'),
    path('order/<int:order_id>/', views.order, name='order'),
    path('start', views.start, name='start'),
    path('process_images', views.process_images, name='process_images'),
]