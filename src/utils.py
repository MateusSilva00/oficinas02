import base64
import re

from fuzzywuzzy import fuzz

from logger import logger
from polls.models import Product

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

def extract_items_from_images(image_top_view, image_front_view):
    """
    Extrai itens das imagens usando a API de visão computacional.
    
    Args:
        image_top_view: Imagem com visão de cima do produto
        image_front_view: Imagem com visão frontal do produto
        
    Returns:
        list: Lista de itens extraídos das imagens
    """
    # Em produção, use a linha abaixo:
    # raw_text = generate_image_description(image_top_view, image_front_view)
    
    # Para desenvolvimento, usando texto de exemplo:
    raw_text = EXAMPLE_IMAGE_PROCESS_RESPONSE
    return decode_items(raw_text)


def compare_items(input_item: str, db_items: Product) -> dict:
    best_score = 0
    best_item = None
    price = 0

    logger.debug(f"Input item: {input_item}")
    for db_item in db_items:
        score = fuzz.ratio(input_item.lower(), db_item.name.lower())
        logger.debug(f"Comparing {input_item} with {db_item.name}: {score}")

        if score > best_score:
            best_score = score
            best_item = db_item.name
            price = db_item.price
            _id = db_item.id
            weight = db_item.avg_weight

    
    return {
        input_item: {
            "best_match": {
                "name": best_item,
                "score": best_score
            },
            "price": price,
            "quantity": extract_quantity(input_item),
            "id": _id,
            "weight": weight
        }
    }

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
    return 1  # Retorna 1 se não encontrar quantidade

def match_items_with_database(items_list):
    """
    Compara itens extraídos com produtos no banco de dados.
    
    Args:
        items_list: Lista de itens para comparar
        
    Returns:
        list: Lista de dicionários com os itens e suas melhores correspondências
    """
    database_items = Product.objects.all()
    matched_items = []

    for input_item in items_list:
        best_match = compare_items(input_item, database_items)
        matched_items.append(best_match)
        
    return matched_items
