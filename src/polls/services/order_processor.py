from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List

from django.http import JsonResponse

from logger import logger
from polls.models import Product  # Adicione esta importação
from polls.services.balance import read_balance
from polls.services.pycamera import image_capture
from utils import extract_items_from_images


class OrderProcessingStrategy(ABC):
    @abstractmethod
    def validate_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_success_message(self) -> str:
        pass

    @abstractmethod
    def get_no_items_message(self) -> str:
        pass


class ProductProcessingStrategy(OrderProcessingStrategy):
    def validate_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Valida produtos gerais - aceita qualquer item."""
        fruit_items = [item for item in items if item.get("is_fruit", False)]

        if fruit_items:
            return {
                "valid": False,
                "message": "Frutas detectadas. Por favor, use a estratégia de processamento de frutas.",
                "filtered_items": [],
            }

        return {"valid": True, "message": "", "filtered_items": items}

    def get_success_message(self) -> str:
        return "Processamento de produtos realizado com sucesso."

    def get_no_items_message(self) -> str:
        return "Nenhum produto foi encontrado nas imagens."


class FruitProcessingStrategy(OrderProcessingStrategy):
    """Estratégia para processamento de frutas - apenas um tipo permitido."""

    def validate_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Valida frutas - apenas um tipo permitido."""
        # Filtrar apenas frutas
        fruit_items = [item for item in items if item.get("is_fruit", False)]

        if not fruit_items:
            return {
                "valid": False,
                "message": "Nenhuma fruta foi detectada na imagem. Por favor, use o botão 'Inserir Produtos' para outros itens.",
                "filtered_items": [],
            }

        # Verificar se há apenas um tipo de fruta
        unique_fruit_names = set(item["name"] for item in fruit_items)

        if len(unique_fruit_names) > 1:
            fruit_list = ", ".join(unique_fruit_names)
            return {
                "valid": False,
                "message": f"Detectados múltiplos tipos de frutas: {fruit_list}. Por favor, coloque apenas um tipo de fruta por vez.",
                "filtered_items": [],
            }

        return {"valid": True, "message": "", "filtered_items": fruit_items}

    def get_success_message(self) -> str:
        return "Processamento de frutas realizado com sucesso."

    def get_no_items_message(self) -> str:
        return "Nenhuma fruta foi encontrada na imagem."


class OrderProcessor:
    """Processador principal que utiliza estratégias."""

    def __init__(self, strategy: OrderProcessingStrategy):
        self.strategy = strategy

    def process_order(self) -> JsonResponse:
        """
        Processa pedido usando a estratégia definida.

        Returns:
            JsonResponse: Resposta JSON com resultado do processamento
        """
        # Capturar imagem
        image_top_view = self._capture_image()

        if not image_top_view:
            return JsonResponse(
                {"error": "Por favor, tire uma foto dos itens."},
                status=400,
            )

        # Extrair itens das imagens
        extracted_items = extract_items_from_images(image_top_view)

        if not extracted_items:
            return JsonResponse(
                {"error": self.strategy.get_no_items_message()},
                status=400,
            )

        # Validar itens usando a estratégia
        validation_result = self.strategy.validate_items(extracted_items)

        if not validation_result["valid"]:
            return JsonResponse(
                {"error": validation_result["message"]},
                status=400,
            )

        total_weight = self._get_total_weight(validation_result["filtered_items"])
        balance_value = read_balance()

        if isinstance(self.strategy, FruitProcessingStrategy):
            fruit_item = validation_result["filtered_items"][0]
            
            fruit_price = float(fruit_item.get("price"))
            fruit_avg = fruit_item.get("avg_weight", 0)
            final_price = (fruit_price * balance_value) / fruit_avg

            validation_result["filtered_items"][0]["price"] = final_price


        output_data = {
            "matched_items": validation_result["filtered_items"],
            "message": self.strategy.get_success_message(),
            "total_weight": total_weight,
            "balance_value": balance_value,
        }
        
        response = JsonResponse(output_data, status=200)
        logger.debug(f"Output data for order processing: {response.content}")

        return response

    def _capture_image(self):
        """Captura imagem da câmera ou retorna imagem de desenvolvimento."""
        # Produção
        return image_capture()

        # Desenvolvimento - descomente a linha abaixo se necessário
        import os

        return os.path.join(
            os.path.dirname(__file__),
            "../static/imgs/orders/fruits_order_type_wrong.jpeg",
        )

    def _get_total_weight(self, items: List[Dict[str, Any]]) -> float:
        """Calcula o peso total dos itens."""
        total_weight = 0
        for item in items:
            if item.get("avg_weight"):
                total_weight += item["avg_weight"]
        return total_weight


class OrderProcessorFactory:
    """Factory para criar processadores com estratégias específicas."""

    STRATEGIES = {
        "product": ProductProcessingStrategy,
        "fruit": FruitProcessingStrategy,
    }

    @classmethod
    def create_processor(cls, order_type: str) -> OrderProcessor:
        if order_type not in cls.STRATEGIES:
            raise ValueError(f"Tipo de pedido não suportado: {order_type}")

        strategy = cls.STRATEGIES[order_type]()
        return OrderProcessor(strategy)
