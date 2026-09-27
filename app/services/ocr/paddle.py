import cv2
import logging
import numpy as np
from paddleocr import PaddleOCR
from app.core.exceptions import DocumentProcessingError
from app.models.ocr import OCRBox, OCRLine, OCRPage
from app.services.ocr.base import OCRProvider

logger = logging.getLogger(__name__)

class PaddleOCRProvider(OCRProvider):
    def __init__(self) -> None:
        try:
            self.engine = PaddleOCR(lang="en")
        except Exception as exc:
            logger.exception("Failed to initialize PaddleOCR.")
            raise DocumentProcessingError(
                "OCR engine initialization failed."
            ) from exc

    def extract_page(self, image: np.ndarray, page_number: int) -> OCRPage:
        try:
            prepared_image = self._prepare_image(image)
            result = self.engine.predict(prepared_image)
        except Exception as exc:
            logger.exception("OCR failed for page %s.", page_number)
            raise DocumentProcessingError(
                f"OCR failed for page {page_number}."
            ) from exc

        lines = []

        for prediction in result:
            data = prediction.json
            payload = data.get("res", data)

            texts = payload.get("rec_texts", [])
            scores = payload.get("rec_scores", [])
            boxes = payload.get("rec_polys", [])

            for text, score, box in zip(texts, scores, boxes):
                cleaned_text = str(text).strip()

                if not cleaned_text:
                    continue

                points = [
                    [float(point[0]), float(point[1])]
                    for point in box
                ]

                lines.append(
                    OCRLine(
                        text=cleaned_text,
                        confidence=float(score),
                        box=OCRBox(points=points),
                    )
                )

        mean_confidence = (
            sum(line.confidence for line in lines) / len(lines)
            if lines
            else 0.0
        )

        return OCRPage(
            page_number=page_number,
            lines=lines,
            mean_confidence=mean_confidence,
        )
    
    @staticmethod
    def _prepare_image(image: np.ndarray) -> np.ndarray:
        if image is None or image.size == 0:
            raise DocumentProcessingError("OCR received an empty image.")

        if image.ndim == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        if image.ndim == 3 and image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        if image.ndim == 3 and image.shape[2] == 3:
            return image

        raise DocumentProcessingError(
            f"Unsupported image shape for OCR: {image.shape}"
        )