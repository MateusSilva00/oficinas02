import os
import sys
from typing import List

import django

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  
django.setup()

from polls.models import Product

ERROR_TOLERANCE = 0.03

def is_expected_weight(balance_given_weight: int, product_list: List[int]) -> bool:
    """
    A função recebe o peso exibida da balança e uma lista de produtos.
    Em seguida, calcula o peso esperado com base no peso dos produtos.
    Se o peso esperado estiver dentro da tolerância do peso dado, retorna True.
    Caso contrário, retorna False.

    # Hipotese
    # A balança exibe o peso total dos produtos, mas a câmera TALVEZ não consiga identificar todos os produtos.
    # Portanto, o peso exibido na balança pode ser MAIOR do que o peso calculado.
    # A tolerância é de 3% do peso esperado.
    # Se o peso exubido na balança for muito maior do que o calculado, é possível que a câmera não tenha identificado todos os produtos.
    # Exemplo:
    # - Peso esperado: 1000g
    # - Peso exibido na balança: 1030g
    # - Tolerância: 3% de 1000g = 30g
    # - Peso exibido na balança está dentro da tolerância, então a câmera pode ter identificado todos os produtos.
    
    # - Peso exibido na balança: 1100g
    # - Tolerância: 3% de 1000g = 30g
    # - Peso exibido na balança está fora da tolerância, então a câmera não identificou todos os produtos.    
    
    Não há possibilidade de o peso exibido na balança ser menor do que o peso esperado, pois a balança exibe o peso total dos produtos.
    """
    
    products = Product.objects.filter(id__in=product_list)
    expected_weight = sum(int(product.avg_weight) for product in products)  # Use avg_weight
    tolerance = expected_weight * ERROR_TOLERANCE

    # Verifica se o peso exibido na balança está dentro da tolerância
    if balance_given_weight <= expected_weight + tolerance:
        return True

    elif balance_given_weight > expected_weight + tolerance:
        # sys.exc_info(
        #     "Peso exibido na balança é MUITO maior do que o peso esperado. A câmera pode não ter identificado todos os produtos."
        # )
        return False

    elif balance_given_weight < expected_weight:
        sys.exc_info(
            "Peso exibido na balança é menor do que o peso esperado. Verifique se a balança está funcionando corretamente."
        )
    



if __name__ == "__main__":
    products = [1, 2, 3]  # Coca Cola, Leite, Chocolate branco oreo (corrigido typo)
    balance_given_weight = 3200

    expected_weight = is_expected_weight(balance_given_weight, products)