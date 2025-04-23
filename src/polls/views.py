from django.http import Http404, HttpResponse
from django.shortcuts import render

from polls.models import Order, Product


def index(request):
    try:
        latest_product_list = Product.objects.order_by('-id')[:5]
    except Product.DoesNotExist:
        raise Http404("No products available.")

    context = {
        'latest_product_list': latest_product_list,
    }
    return render(request, 'polls/index.html', context)


def start(request):
    return render(request, 'polls/start.html')

def product(request, product_id):
    latest_product = Product.objects.get(id=product_id)
    output = f"You're looking at product {latest_product.name} with price R${latest_product.price}."
    return HttpResponse(output)

def order(request, order_id):
    latest_order = Order.objects.get(id=order_id)
    product = latest_order.product
    output = f"You're looking at order {latest_order.id} of {latest_order.quantity} {product.name}(s) with total price R${latest_order.total_price}."

    return HttpResponse(output)