import cv2
import numpy as np

def rotate_image(
    image: np.ndarray,
    angle: int,
) -> np.ndarray:

    normalized_angle = angle % 360

    if normalized_angle == 90:
        return cv2.rotate(
            image,
            cv2.ROTATE_90_CLOCKWISE,
        )

    if normalized_angle == 180:
        return cv2.rotate(
            image,
            cv2.ROTATE_180,
        )

    if normalized_angle == 270:
        return cv2.rotate(
            image,
            cv2.ROTATE_90_COUNTERCLOCKWISE,
        )

    return image