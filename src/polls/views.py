import os

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
#from pypix.core.styles.border_styles import BorderStyle
#from pypix.core.styles.frame_styles import FrameStyle
#from pypix.core.styles.line_styles import LineStyle
#from pypix.core.styles.marker_styles import MarkerStyle
#from pypix.core.styles.qr_styler import GradientMode
#from pypix.pix import Pix

from polls.models import Order, Product
from polls.services.order_processor import OrderProcessorFactory


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


def generate_pix(request):
    return 0
    value = request.GET.get("value")
    if not value:
        return JsonResponse({"error": "Valor não fornecido"}, status=400)

    # Criar diretório para QR codes se não existir
    qr_dir = os.path.join(settings.BASE_DIR, "polls", "static", "polls", "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)

    # Definir o caminho completo para salvar a imagem
    output_path = os.path.join(qr_dir, "pix_qrcode.png")
    print(f"Gerando QR Code PIX com valor: {value} em {output_path}")

    pix = Pix()
    pix.set_name_receiver("Mateus Silva")
    pix.set_city_receiver("Curitiba")
    pix.set_key("8f700b89-48e6-43db-8ef3-135c66948233")
    pix.set_description("Pagamento de produtos")
    pix.set_amount(float(value))

    br_code = pix.get_br_code()

    pix.save_qrcode(
        data=br_code,
        output=output_path,
        box_size=7,
        border=1,
        marker_style=MarkerStyle.QUARTER_CIRCLE,
        border_style=BorderStyle.ROUNDED,
        line_style=LineStyle.ROUNDED,
        gradient_color="purple",
        gradient_mode=GradientMode.NORMAL,
        frame_style=FrameStyle.SCAN_ME_PURPLE,
        style_mode="Full",
    )
    print(f"QR Code gerado com sucesso em: {output_path}")

    # Retornar a imagem como resposta
    if os.path.exists(output_path):
        return FileResponse(open(output_path, "rb"), content_type="image/png")
    else:
        return JsonResponse(
            {"error": f"Falha ao criar arquivo QR code: {output_path} não existe"},
            status=500,
        )
