import cv2
import numpy as np
from app.services.ocr.paddle import PaddleOCRProvider

def main():
    image = np.ones((300, 800, 3), dtype=np.uint8) * 255

    cv2.putText(
        image,
        "INVOICE INV-1001",
        (50, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 0, 0),
        3,
        cv2.LINE_AA,
    )

    provider = PaddleOCRProvider()

    result = provider.extract_page(
        image=image,
        page_number=1,
    )

    print(f"Mean confidence: {result.mean_confidence:.3f}")

    for line in result.lines:
        print(f"{line.text} ({line.confidence:.3f})")

if __name__ == "__main__":
    main()