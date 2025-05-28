import base64
import re
import logging

from logger import logger
from polls.models import Product
from polls.services.openai_api import generate_image_description

logger = logging.getLogger(__name__)

EXAMPLE_IMAGE_PROCESS_RESPONSE = """
- 2 caixas de leite Italac Semi 1%
- 1 garrafa de Coca-Cola
- 1 pacote de pão Wickbold
- 1 barra de chocolate Lacta Laka Oreo
- 1 lata de cerveja Brahma
- 1 lata de cerveja Skol
""" 


def encode_image(image):
    if isinstance(image, str):
        logger.debug(f"Encoding local image: {image}")
        with open(image, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    else:
        logger.debug("Encoding uploaded image.")
        image.seek(0)
        return base64.b64encode(image.read()).decode('utf-8')
    

def decode_items(text: str) -> list:
    items = text.split("\n")
    items = [item.strip() for item in items if item.strip()]
    items = [item.replace("-", "").strip() for item in items]

    return items


def get_products_from_database():
    """
    Busca todos os produtos no banco de dados e retorna um contexto detalhado para o GPT.
    """
    products = Product.objects.all()
    context = ""
    for produto in products:
        context += f"Produto: {produto.name}\n"
        context += f"Descrição: {produto.description}\n"
        context += f"Etiqueta: {produto.label}\n"
        context += f"Preço: {produto.price}\n"
        context += f"Peso Médio: {produto.avg_weight}\n"
        context += "\n"  
    return context

# Função principal para extrair os itens das imagens
def extract_items_from_images(image_top_view, image_front_view):
    """
    Extrai itens das imagens usando o contexto completo do banco de dados e a API do GPT.

    Returns:
        list: Lista de itens extraídos das imagens
    """
    # Codificar as imagens em base64
    base64_top_view = encode_image(image_top_view)
    base64_front_view = encode_image(image_front_view)

    # Obter o contexto completo do banco de dados
    context = get_products_from_database()

    # Construir a string de entrada (input) para o GPT
    input_text = f"{context}\nAqui estão as duas imagens:"

    # Enviar o contexto ao GPT, junto com as imagens codificadas
    raw_dict = generate_image_description(
        base64_front_view=base64_front_view, 
        base64_top_view=base64_top_view, 
        input_text=input_text
    )
    
    logger.debug(f"Raw response from OpenAI: {raw_dict}")

    raw_text = raw_dict["output"][0]["content"][0]["text"]
    logger.debug(f"Raw text from OpenAI:\n{raw_text}")

    # Decodificar os itens extraídos a partir da resposta do GPT
    items_list = decode_items(raw_text)

    # Usar a função match_items_with_database para comparar os itens extraídos com os produtos no banco
    matched_items = match_items_with_database(items_list)

    return matched_items



def compare_items(raw_text, db_item: Product) -> bool:
    """
    Compara o texto extraído do GPT com os dados do banco de dados para verificar se o produto está correto.
    
    Args:
        raw_text (str): Texto extraído do GPT com a descrição do produto.
        db_item (Product): Produto do banco de dados.

    Returns:
        bool: Retorna True se o produto do banco de dados corresponder ao produto identificado pelo GPT.
    """
    # Garantir que o atributo 'name' existe e é uma string
    if db_item.name and isinstance(db_item.name, str):
        # Comparar o nome do produto com o texto extraído (ignorando maiúsculas/minúsculas)
        if db_item.name.lower() in raw_text.lower():
            return True
    return False


def extract_quantity(item: str) -> int:
    """
    Extrai a quantidade de um item a partir de uma string.
    
    Args:
        item: String representando o item
        
    Returns:
        int: Quantidade do item
    """
    match = re.search(r'(\d+)', item)
    if match:
        return int(match.group(1))
    return 1 

def match_items_with_database(items_list):
    """
    Compara os itens extraídos com os produtos no banco de dados e permite múltiplas correspondências.

    Args:
        items_list: Lista de itens extraídos pela API do GPT.
        
    Returns:
        list: Lista de dicionários com os itens e suas correspondências (vários produtos podem ser encontrados por item).
    """
    database_items = Product.objects.all()
    matched_items = []

    for input_item in items_list:
        item_matches = []  # Lista para armazenar as correspondências de produtos para cada item
        for db_item in database_items:
            if compare_items(input_item, db_item):  # Passar um único produto para a função de comparação
                item_matches.append(db_item)  # Adicionar o produto correspondente à lista de matches
        if item_matches:
            matched_items.append({
                'item': input_item,  # Guardando o item extraído
                'matches': item_matches  # Guardando todos os produtos correspondentes encontrados
            })

    return matched_items