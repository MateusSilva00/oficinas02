from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from polls.models import Order, Product
from polls.services.pycamera import image_capture
from utils import extract_items_from_images, match_items_with_database


def index(request):
    """Renderiza a página inicial com a lista de produtos."""
    try:
        latest_product_list = Product.objects.all()
    except Product.DoesNotExist:
        raise Http404("No products available.")

    context = {
        'latest_product_list': latest_product_list,
    }
    return render(request, 'polls/index.html', context)


def start(request):
    """Renderiza a página de início do processamento de compras."""
    return render(request, 'polls/start.html')


def checkout(request):
    """Renderiza a página de checkout para finalizar a compra."""
    return render(request, 'polls/checkout.html')


@require_POST
def process_images(request) -> JsonResponse:
    """
    Processa imagens enviadas pelo usuário, extrai itens e compara com o banco de dados.
    
    Args:
        request: Requisição HTTP com as imagens
        
    Returns:
        JsonResponse: Resposta JSON com os itens extraídos e suas correspondências
    """
    
    image_front_view = image_capture(frontal=True)
    image_top_view = image_capture()

    if not image_top_view or not image_front_view:
        return HttpResponse("Please upload both images.")
    
    items = extract_items_from_images(image_top_view, image_front_view)

    if not items:
        return JsonResponse(
            {
                'items': [],
                'message': "No items found in the images.",
            },
            status=400,
        )
    
    matched_items = match_items_with_database(items)

    return JsonResponse(
        {
            'items': items,
            'matched_items': matched_items,
            'message': "Image processing successful.",
        },
        status=200,
    )
    
@csrf_exempt
@require_POST
def compare_items_api(request):
    """
    Endpoint da API para comparar itens fornecidos com produtos do banco de dados.
    
    Args:
        request: Requisição HTTP com a lista de itens para comparar
        
    Returns:
        JsonResponse: Resposta JSON com os itens e suas correspondências
    """
    inputs_items = request.POST.getlist('items[]') 
    
    if not inputs_items:
        return JsonResponse(
            {
                'error': "No items provided.",
            },
            status=400,
        )
    
    matched_items = match_items_with_database(inputs_items)

    return JsonResponse(
        {
            'items': matched_items,
            'message': "Item comparison successful.",
        },
        status=200,
    )


def product(request, product_id):
    """Exibe informações de um produto específico."""
    latest_product = Product.objects.get(id=product_id)
    output = f"You're looking at product {latest_product.name} with price R${latest_product.price}."
    return HttpResponse(output)


def order(request, order_id):
    """Exibe informações de um pedido específico."""
    latest_order = Order.objects.get(id=order_id)
    product = latest_order.product
    output = f"You're looking at order {latest_order.id} of {latest_order.quantity} {product.name}(s) with total price R${latest_order.total_price}."
    return HttpResponse(output)