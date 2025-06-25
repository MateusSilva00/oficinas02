from django.urls import path

from polls import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name="index"),
    path("start/", views.start, name="start"),
    path("checkout/", views.checkout, name="checkout"),
    path("process_images/", views.process_order, name="process_images"),
    path("process_fruits/", views.process_fruit_order, name="process_fruits"),
    path("product/<int:product_id>/", views.product, name="product"),
    path("order/<int:order_id>/", views.order, name="order"),
    path("gerar_qr_pix/", views.gerar_qr_pix, name="gerar_qr_pix"),
]
