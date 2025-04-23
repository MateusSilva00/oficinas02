import base64

from logger import logger


def encode_image(image):
    if isinstance(image, str):
        logger.debug(f"Encoding local image: {image}")
        with open(image, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    else:
        logger.debug("Encoding uploaded image.")
        image.seek(0)
        return base64.b64encode(image.read()).decode('utf-8')