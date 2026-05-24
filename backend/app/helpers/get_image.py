import random
import base64
import os
from helpers.logger import logger

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images")


def get_random_image_url():
    try:
        random_number = random.randint(1, 169)
        image_path = os.path.join(IMAGES_DIR, f"{random_number}.jpg")
        with open(image_path, "rb") as f:
            binary_data = f.read()
        base64_string = base64.b64encode(binary_data).decode("utf-8")
        return base64_string
    except Exception as e:
        logger.error(f"Error getting local image: {str(e)}")
        return None
