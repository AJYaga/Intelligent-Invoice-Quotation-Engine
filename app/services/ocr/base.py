from abc import ABC, abstractmethod
import numpy as np
from app.models.ocr import OCRPage

class OCRProvider(ABC):
    @abstractmethod
    def extract_page(self, image: np.ndarray, page_number: int) -> OCRPage:
        raise NotImplementedError