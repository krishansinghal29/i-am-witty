from helpers.get_image import get_random_image_url
import json


class ImageGenerator():
    def process(self) -> str:
        image_url = get_random_image_url()
        response_array = [{"role": "Image", "content": f"data:image/jpeg;base64,{image_url}"}]
        return json.dumps({"question": response_array})
