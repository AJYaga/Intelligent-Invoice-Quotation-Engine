import cv2
import numpy as np
from app.core.exceptions import InvalidDocumentError

def decode_image(file_bytes: bytes) -> np.ndarray:
    buffer = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    if image is None:
        raise InvalidDocumentError(
            "Unable to decode image. The file may be corrupt or invalid."
        )

    return image

def preprocess_image(image: np.ndarray) -> np.ndarray:
    if image is None or image.size == 0:
        raise InvalidDocumentError("Image is empty or invalid.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(
        gray,
        None,
        h=10,
        templateWindowSize=7,
        searchWindowSize=21,
    )

    enhanced = cv2.equalizeHist(denoised)
    return enhanced