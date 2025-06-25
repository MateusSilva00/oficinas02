import base64
import re
from typing import Dict, List, Optional

from logger import logger
from polls.models import Product
from polls.services.openai_api import generate_image_description

EXAMPLE_IMAGE_PROCESS_RESPONSE = """
- [1] [2] 
- [2] [1] 
- [3] [3] 
"""


def encode_image(image):
    if isinstance(image, str):
        logger.debug(f"Encoding local image: {image}")
        with open(image, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    else:
        logger.debug("Encoding uploaded image.")
        image.seek(0)
        return base64.b64encode(image.read()).decode("utf-8")


def decode_items_in_dict(text: str) -> dict:
    """
    O GPT retorna uma lista de itens no seguinte formato:
    - [1] [2]
    - [2] [1]

    Esta função decodifica esses itens em um dicionário onde a chave é o ID do produto e o valor é a quantidade.
    Args:
        text (str): Texto retornado pelo GPT contendo os itens.
    Returns:
        dict: Dicionário com os IDs dos produtos como chaves e as quantidades como valores.
    """

    items = {}
    lines = text.strip().split("\n")
    for line in lines:
        match = re.match(r"- \[(\d+)\] \[(\d+)\]", line)
        if match:
            product_id = int(match.group(1))
            quantity = int(match.group(2))
            items[product_id] = quantity
    return items


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
def extract_items_from_images(
    image_top_view, image_front_view=Optional[str]
) -> List[dict]:
    """
    Extrai itens das imagens usando o contexto completo do banco de dados e a API do GPT.

    Returns:
        list: Lista de itens extraídos das imagens
    """
    # Codificar as imagens em base64
    base64_top_view = encode_image(image_top_view)
    # base64_front_view = encode_image(image_front_view)

    # Obter o contexto completo do banco de dados
    context = get_products_from_database()

    logger.debug(f"Context for GPT:\n{context}")

    # Construir a string de entrada (input) para o GPT
    input_text = f"{context}\nCom base neste banco de dados me retorne somente o ID dos produtos identifcados. Caso nada seja encontrado, não me retorne nada. A sua resposta deve ser uma lista de itens, cada item em uma linha, represetando productId e a quantidade visualizada, no seguinte formato:\n{EXAMPLE_IMAGE_PROCESS_RESPONSE}\n\n"
    # Enviar o contexto ao GPT, junto com as imagens codificadas
    raw_response = generate_image_description(
        # base64_front_view=base64_front_view,
        base64_top_view=base64_top_view,
        input_text=input_text,
    )

    logger.debug(f"Raw response from OpenAI: {raw_response}")

    raw_text = raw_response["output"][0]["content"][0]["text"]
    logger.debug(f"Raw text from OpenAI:\n{raw_text}")

    # Decodificar os itens extraídos a partir da resposta do GPT
    extracted_product_ids = decode_items_in_dict(raw_text)
    logger.debug(f"Extracted product IDs: {extracted_product_ids.keys()}")

    # Usar a função match_items_with_database para comparar os itens extraídos com os produtos no banco
    matched_items = match_items_with_database(extracted_product_ids)

    return matched_items


def extract_quantity(item: str) -> int:
    """
    Extrai a quantidade de um item a partir de uma string.

    Args:
        item: String representando o item

    Returns:
        int: Quantidade do item
    """
    match = re.search(r"(\d+)", item)
    if match:
        return int(match.group(1))
    return 1


def match_items_with_database(items_object: Dict[int, int]) -> List[dict]:
    """
    Rebece um dicionário de IDs de produtos e quantidades, e retorna uma lista de dicionários com os itens correspondentes no banco de dados.

    Args:
        items_object (Dict[int, int]): Dicionário onde a chave é o ID do produto e o valor é a quantidade.

    Returns:
        List[dict]: Lista de dicionários com os detalhes dos produtos correspondentes.

    """
    matched_items = []
    for item_id, quantity in items_object.items():
        database_item = Product.objects.filter(id=item_id).first()

        if database_item:
            found_item = {
                "id": database_item.id,
                "name": database_item.name,
                "description": database_item.description,
                "label": database_item.label,
                "price": database_item.price,
                "avg_weight": database_item.avg_weight,
                "quantity": quantity,
                "is_fruit": database_item.is_fruit,
            }

            matched_items.append(found_item)

    logger.debug(f"Matched items: {matched_items}")
    return matched_items


def gerar_payload_pix(chave, nome, cidade, valor, txid="***"):
    from pypix import Pix

    pix = Pix(chave=chave, nome=nome, cidade=cidade, valor=valor, txid=txid)
    return pix.payload()
