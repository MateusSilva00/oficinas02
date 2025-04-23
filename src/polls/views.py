from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from polls.models import Order, Product
from polls.services.openai_api import generate_image_description


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


@require_POST
def process_images(request):
    image_top_view = request.FILES.get('image1')
    image_front_view = request.FILES.get('image2')

    if not image_top_view or not image_front_view:
        return HttpResponse("Please upload both images.")
    
    response = generate_image_description(image_top_view, image_front_view)

    if response:
        return JsonResponse(
            response,
            status=200,
        )
    else:
        return HttpResponse("Image processing failed.")

def product(request, product_id):
    latest_product = Product.objects.get(id=product_id)
    output = f"You're looking at product {latest_product.name} with price R${latest_product.price}."
    return HttpResponse(output)

def order(request, order_id):
    latest_order = Order.objects.get(id=order_id)
    product = latest_order.product
    output = f"You're looking at order {latest_order.id} of {latest_order.quantity} {product.name}(s) with total price R${latest_order.total_price}."

    return HttpResponse(output)