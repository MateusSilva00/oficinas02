import os

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from polls.models import Order, Product
from polls.services.pycamera import image_capture
from utils import (
    extract_items_from_images,
    gerar_payload_pix,
    match_items_with_database,
)


def index(request):
    """Renderiza a página inicial com a lista de produtos."""
    try:
        latest_product_list = Product.objects.all()
    except Product.DoesNotExist:
        raise Http404("No products available.")

    context = {
        "latest_product_list": latest_product_list,
    }
    return render(request, "polls/index.html", context)


def start(request):
    """Renderiza a página de início do processamento de compras."""
    return render(request, "polls/start.html")


def checkout(request):
    """Renderiza a página de checkout para finalizar a compra."""
    return render(request, "polls/checkout.html")


@require_POST
def process_order(request) -> JsonResponse:
    """
    Processa imagens enviadas pelo usuário, extrai itens e compara com o banco de dados.

    Args:
        request: Requisição HTTP com as imagens

    Returns:
        JsonResponse: Resposta JSON com os itens extraídos e suas correspondências
    """

    # Produção
    # image_front_view = image_capture(frontal=True)
    image_top_view = image_capture()

    # Desenvolvimento
    # PATH TO IMAGE = src/polls/static/imgs/orders/IMG-20250503-WA0044.jpg
    # image_top_view = os.path.join(
    #     os.path.dirname(__file__), "static/imgs/orders/IMG-20250503-WA0044.jpg"
    # )

    if not image_top_view:
        return HttpResponse("Please upload images.")

    matched_items = extract_items_from_images(image_top_view)

    if not matched_items:
        return JsonResponse(
            {
                "items": [],
                "message": "No items found in the images.",
            },
            status=400,
        )

    return JsonResponse(
        {
            "matched_items": matched_items,
            "message": "Image processing successful.",
        },
        status=200,
    )

@require_POST
def process_fruit_order(request) -> JsonResponse:
    """
    Processa imagens de frutas, validando que apenas um tipo de fruta foi detectado.

    Args:
        request: Requisição HTTP para processamento de frutas

    Returns:
        JsonResponse: Resposta JSON com os itens de fruta ou erro se múltiplos tipos
    """
    # Produção
    # image_top_view = image_capture()

    # Desenvolvimento
    # PATH TO IMAGE = src/polls/static/imgs/orders/IMG-20250503-WA0044.jpg
    image_top_view = os.path.join(
        os.path.dirname(__file__), "static/imgs/orders/fruits_order_type_correct_apple.jpeg"
    )


    if not image_top_view:
        return JsonResponse(
            {
                "error": "Por favor, tire uma foto das frutas.",
            },
            status=400,
        )

    matched_items = extract_items_from_images(image_top_view)

    if not matched_items:
        return JsonResponse(
            {
                "error": "Nenhuma fruta foi encontrada na imagem.",
            },
            status=400,
        )

    fruit_items = []
    for item in matched_items:
        if item.get("is_fruit", False):
            fruit_items.append(item)

    
    if not fruit_items:
        return JsonResponse(
            {
                "error": "Nenhuma fruta foi detectada na imagem. Por favor, use o botão 'Inserir Produtos' para outros itens.",
            },
            status=400,
        )

    # Verificar se há apenas um tipo de fruta
    unique_fruit_names = set(item['name'] for item in fruit_items)
    
    if len(unique_fruit_names) > 1:
        fruit_list = ", ".join(unique_fruit_names)
        return JsonResponse(
            {
                "error": f"Detectados múltiplos tipos de frutas: {fruit_list}. Por favor, coloque apenas um tipo de fruta por vez.",
            },
            status=400,
        )

    return JsonResponse(
        {
            "matched_items": fruit_items,
            "message": "Processamento de frutas realizado com sucesso.",
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


def gerar_qr_pix(request):
    valor = request.GET.get('valor')
    if not valor:
        return JsonResponse({'error': 'Valor não fornecido'}, status=400)
    
    # Configuração do Pix
    chave_pix = "searaujor7@gmail.com"  # Substitua pela sua chave Pix válida
    nome_recebedor = "Sebastiao Araujo"
    cidade_recebedor = "Curitiba"
    descricao = "Pagamento"

    # Estrutura do payload Pix
    payload = (
        f"000201"  # Identificador do formato
        f"010211"  # Identificador do método de pagamento (Pix)
        f"26580014BR.GOV.BCB.PIX"  # Domínio do Pix
        f"0136{chave_pix}"  # Chave Pix
        f"52040000"  # Código do país
        f"5303986"  # Moeda (986 = BRL)
        f"5405{valor}"  # Valor da transação
        f"5802BR"  # País
        f"5908{nome_recebedor}"  # Nome do recebedor
        f"6009{cidade_recebedor}"  # Cidade do recebedor
        f"6304"  # CRC16 será calculado abaixo
    )
    
    # Função para calcular o CRC16
    def calcular_crc16(payload):
        polinomio = 0x1021
        resultado = 0xFFFF
        for byte in payload.encode('utf-8'):
            resultado ^= (byte << 8)
            for _ in range(8):
                if (resultado & 0x8000):
                    resultado = (resultado << 1) ^ polinomio
                else:
                    resultado <<= 1
            resultado &= 0xFFFF
        return f"{resultado:04X}"

    # Adicionar o CRC16 ao payload
    payload += calcular_crc16(payload)
    
    return JsonResponse({'payload': payload})

