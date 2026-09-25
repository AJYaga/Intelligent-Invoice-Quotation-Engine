from app.models.ocr import OCRResult
from app.models.preprocessing import PreprocessingResult
from app.services.ocr.base import OCRProvider

class OCRService:
    def __init__(self, provider: OCRProvider) -> None:
        self.provider = provider

    def extract_document(self, preprocessing_result: PreprocessingResult) -> OCRResult:
        pages = []

        for page in preprocessing_result.pages:
            ocr_page = self.provider.extract_page(
                image=page.image,
                page_number=page.page_number,
            )
            pages.append(ocr_page)

        all_text = []
        all_confidences = []

        for page in pages:
            for line in page.lines:
                all_text.append(line.text)
                all_confidences.append(line.confidence)

        full_text = "\n".join(all_text)
        mean_confidence = (
            sum(all_confidences) / len(all_confidences)
            if all_confidences
            else 0.0
        )

        return OCRResult(
            pages=pages,
            full_text=full_text,
            mean_confidence=mean_confidence,
        )