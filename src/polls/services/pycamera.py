import os
import cv2
from logger import logger

BASE_PATH = "orders/imgs"

def image_capture(order_id: int = 10, frontal: bool = False) -> str:
    """
    Capture an image from the webcam and save it to a file.
    """
    # Verificar se o diretório existe, se não, criar
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

    # Abrir a câmera padrão (0)
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise IOError("Cannot open webcam")

    ret, frame = camera.read()

    if not ret:
        raise IOError("Cannot capture frame")

    position = "frontal" if frontal else "top"
    filename = f"captured_image_{order_id}_{position}.jpg"
    filepath = f"{BASE_PATH}/{filename}"

    # Salvar a imagem
    cv2.imwrite(filepath, frame)

    logger.debug(f"Image saved as {filepath}")

    # Liberar a câmera
    camera.release()

    return filepath
