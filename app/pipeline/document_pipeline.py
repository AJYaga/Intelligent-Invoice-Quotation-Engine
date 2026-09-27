from dataclasses import dataclass
from app.models.classification import ClassificationResult
from app.models.extraction import ExtractionResult
from app.models.ocr import OCRResult
from app.models.validation import ValidationResult
from app.services.classification.classifier import DocumentClassifier
from app.services.extraction.service import ExtractionService
from app.services.ocr.paddle import PaddleOCRProvider
from app.services.ocr.service import OCRService
from app.services.preprocessing.processor import preprocess_document
from app.services.validation.service import ValidationService

@dataclass
class PipelineResult:
    ocr: OCRResult
    classification: ClassificationResult
    extraction: ExtractionResult
    validation: ValidationResult

class DocumentPipeline:
    def __init__(self) -> None:
        self.ocr_service = OCRService(
            provider=PaddleOCRProvider()
        )
        self.classifier = DocumentClassifier()
        self.extraction_service = ExtractionService()
        self.validation_service = ValidationService()

    def analyze(
        self,
        file_bytes: bytes,
        filename: str,
    ) -> PipelineResult:
        preprocessing = preprocess_document(
            file_bytes=file_bytes,
            filename=filename,
        )

        ocr_result = self.ocr_service.extract_document(
            preprocessing
        )

        classification = self.classifier.classify(
            ocr_result
        )

        extraction = self.extraction_service.extract(
            ocr_result
        )

        validation = self.validation_service.validate(
            ocr_result=ocr_result,
            classification=classification,
            extraction=extraction,
        )

        return PipelineResult(
            ocr=ocr_result,
            classification=classification,
            extraction=extraction,
            validation=validation,
        )