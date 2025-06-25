import os

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from polls.models import Order, Product
from polls.services.order_processor import OrderProcessorFactory
from utils import match_items_with_database


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
    Processa imagens de produtos gerais enviadas pelo usuário.

    Args:
        request: Requisição HTTP com as imagens

    Returns:
        JsonResponse: Resposta JSON com os itens extraídos e suas correspondências
    """
    try:
        processor = OrderProcessorFactory.create_processor("product")
        return processor.process_order()
    except Exception as e:
        return JsonResponse(
            {"error": f"Erro interno no processamento: {str(e)}"},
            status=500,
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
    try:
        processor = OrderProcessorFactory.create_processor("fruit")
        return processor.process_order()
    except Exception as e:
        return JsonResponse(
            {"error": f"Erro interno no processamento: {str(e)}"},
            status=500,
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
    valor = request.GET.get("valor")
    if not valor:
        return JsonResponse({"error": "Valor não fornecido"}, status=400)

    # Configuração do Pix
    chave_pix = "searaujor7@gmail.com"  # Substitua pela sua chave Pix válida
    nome_recebedor = "Sebastiao Araujo"
    cidade_recebedor = "Curitiba"

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
        for byte in payload.encode("utf-8"):
            resultado ^= byte << 8
            for _ in range(8):
                if resultado & 0x8000:
                    resultado = (resultado << 1) ^ polinomio
                else:
                    resultado <<= 1
            resultado &= 0xFFFF
        return f"{resultado:04X}"

    # Adicionar o CRC16 ao payload
    payload += calcular_crc16(payload)

    return JsonResponse({"payload": payload})
