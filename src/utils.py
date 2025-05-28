import base64
import logging
import re
from typing import List

from logger import logger
from polls.models import Product
from polls.services.openai_api import generate_image_description

logger = logging.getLogger(__name__)

EXAMPLE_IMAGE_PROCESS_RESPONSE = """
- Quantidade: 2 - ProdutoId: 1
- Quantidade: 1 - ProdutoId: 2
- Quantidade: 3 - ProdutoId: 3
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
    

def decode_items_in_productId(text: str) -> list:
    items = text.split("\n")
    products_ids = []
    for item in items:
        item = item.strip()
        if item:
            # Verifica se o item contém a palavra "ProdutoId" e extrai o ID
            match = re.search(r'ProdutoId:\s*(\d+)', item)
            if match:
                products_ids.append(int(match.group(1)))

    return products_ids


def get_products_from_database():
    """
    Busca todos os produtos no banco de dados e retorna um contexto detalhado para o GPT.
    """
    products = Product.objects.all()
    context = ""
    for produto in products:
        context += f"ID: {produto.id}\n"
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

    print(f"Context for GPT:\n{context}")
    logger.debug(f"Context for GPT:\n{context}")

    # Construir a string de entrada (input) para o GPT
    input_text = f"{context}\nCom base neste banco de dados me retorne somente o ID dos produtos identifcados. Caso nada seja encontrado, não me retorne nada. A sua resposta deve ser uma lista de itens, cada item em uma linha, no seguinte formato:\n{EXAMPLE_IMAGE_PROCESS_RESPONSE}\n\n" \

    # Enviar o contexto ao GPT, junto com as imagens codificadas
    raw_dict = generate_image_description(
        base64_front_view=base64_front_view, 
        base64_top_view=base64_top_view, 
        input_text=input_text
    )
    
    logger.debug(f"Raw response from OpenAI: {raw_dict}")
    print(f"Raw response from OpenAI: {raw_dict}")

    raw_text = raw_dict["output"][0]["content"][0]["text"]
    logger.debug(f"Raw text from OpenAI:\n{raw_text}")
    print(f"Raw text from OpenAI:\n{raw_text}")

    # Decodificar os itens extraídos a partir da resposta do GPT
    items_ids = decode_items_in_productId(raw_text)
    print(f"Product ID's from GPT response: {items_ids}")

    # Usar a função match_items_with_database para comparar os itens extraídos com os produtos no banco
    matched_items = match_items_with_database(items_ids)

    return matched_items



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

def match_items_with_database(items_id_list: List[int]) -> List[dict]:
    """
    Compara os itens extraídos com os produtos no banco de dados e permite múltiplas correspondências.

    Args:
        items_list: Lista de itens extraídos pela API do GPT.
        
    Returns:
        list: Lista de dicionários com os itens e suas correspondências (vários produtos podem ser encontrados por item).
    """
    matched_items = []
    for item_id in items_id_list:
        database_item = Product.objects.filter(id=item_id).first()
        
        if database_item:
            found_item = {
                'id': database_item.id,
                'name': database_item.name,
                'description': database_item.description,
                'label': database_item.label,
                'price': database_item.price,
                'avg_weight': database_item.avg_weight
            }
        
            matched_items.append(found_item)

    print(f"Matched items: {matched_items}")
    logger.debug(f"Matched items: {matched_items}")
    return matched_items